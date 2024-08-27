from models import db, Subshell, ElectronCfg


def calculate_electron_configuration(atomic_number):
    subshells = db.session.query(Subshell).order_by(Subshell.id).all()
    configuration = []
    electrons_remaining = atomic_number
    # Distribute electrons across subshells
    for subshell in subshells:
        if electrons_remaining <= 0:
            break
        electrons_in_subshell = min(electrons_remaining, subshell.maxelectrons)
        pqn = int(subshell.subshells[0])  # Principal Quantum Number
        subshell_type = subshell.subshells[1]  # s, p, d, or f
        config = {
            'pqn': pqn,
            'subshell_id': subshell.id,
            'element_id': atomic_number,
            subshell_type: electrons_in_subshell
        }
        configuration.append(config)
        electrons_remaining -= electrons_in_subshell
    # Combine configurations for subshells with the same ID
    final_configuration = {}
    for config in configuration:
        subshell_id = config['subshell_id']
        if subshell_id in final_configuration:
            for key in ['s', 'p', 'd', 'f']:
                if key in config:
                    if key in final_configuration[subshell_id]:
                        final_configuration[subshell_id][key] += config[key]
                    else:
                        final_configuration[subshell_id][key] = config[key]
        else:
            final_configuration[subshell_id] = config
    # Generate a string representation of the electron configuration
    config_string = ""
    for config in final_configuration.values():
        for subshell in ['s', 'p', 'd', 'f']:
            if subshell in config and config[subshell] > 0:
                config_string += (f"{config['pqn']}{subshell}"
                                  f"<sup>{config[subshell]}</sup> ")
    return final_configuration, config_string.strip()


def store_electron_configuration(element_id, configuration):
    # Remove existing configurations for the element
    db.session.query(ElectronCfg).filter_by(element_id=element_id).delete()
    # Add new configurations
    for subshell_id, config in configuration.items():
        electron_cfg = ElectronCfg(
            element_id=element_id,
            subshell_id=config['subshell_id'],
            pqn=config['pqn'],
            s=config.get('s'),
            p=config.get('p'),
            d=config.get('d'),
            f=config.get('f')
        )
        db.session.add(electron_cfg)
    db.session.commit()


def determine_state_at_zero(element, norm_temp):
    return determine_state_at_temperature(element, norm_temp)


def determine_state_at_temperature(element, temperature):
    try:
        # Convert melting and boiling points to integers, or None if 'N/A'
        meltingpoint = (int(element.meltingpoint)
                        if element.meltingpoint != 'N/A' else None)
        boilingpoint = (int(element.boilingpoint)
                        if element.boilingpoint != 'N/A' else None)
    except ValueError:
        return "unknown"
    # Determine state based on temperature and phase transition points
    if meltingpoint is None:
        return "unknown"
    if boilingpoint is None:
        return "solid" if meltingpoint > temperature else "liquid"
    if meltingpoint > temperature:
        return "solid"
    if meltingpoint <= temperature < boilingpoint:
        return "liquid"
    return "gas"
