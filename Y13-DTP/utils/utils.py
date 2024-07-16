# utils.py
from models import db, Subshell, ElectronCfg

# Function to calculate electron configuration
def calculate_electron_configuration(atomic_number):
    subshells = db.session.query(Subshell).order_by(Subshell.id).all()
    configuration = []
    electrons_remaining = atomic_number
    for subshell in subshells:
        if electrons_remaining <= 0:
            break
        electrons_in_subshell = min(electrons_remaining, subshell.maxelectrons)
        pqn = int(subshell.subshells[0])
        subshell_type = subshell.subshells[1]
        config = {
            'pqn': pqn,
            'subshell_id': subshell.id,
            'element_id': atomic_number,
            subshell_type: electrons_in_subshell
        }
        configuration.append(config)
        electrons_remaining -= electrons_in_subshell
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
    config_string = ""
    for config in final_configuration.values():
        for subshell in ['s', 'p', 'd', 'f']:
            if subshell in config and config[subshell] > 0:
                config_string += f"{config['pqn']}{subshell}<sup>{config[subshell]}</sup> "
    return final_configuration, config_string.strip()

# Function to store electron configuration in the database
def store_electron_configuration(element_id, configuration):
    db.session.query(ElectronCfg).filter_by(element_id=element_id).delete()
    for subshell_id, config in configuration.items():
        electron_cfg = ElectronCfg(
            element_id=element_id,
            subshell_id=config['subshell_id'],
            pqn=config['pqn'],
            s=config.get('s', None),
            p=config.get('p', None),
            d=config.get('d', None),
            f=config.get('f', None)
        )
        db.session.add(electron_cfg)
    db.session.commit()

# Function to determine the state of an element at 273 Kelvin (0 Celsius)
def determine_state_at_zero(element):
    try:
        meltingpoint = int(element.meltingpoint) if element.meltingpoint != 'N/A' else None
        boilingpoint = int(element.boilingpoint) if element.boilingpoint != 'N/A' else None
    except ValueError:
        return "unknown"
    if meltingpoint is None:
        return "unknown"
    elif boilingpoint is None:
        return "solid" if meltingpoint > 273 else "liquid"
    elif meltingpoint > 273:
        return "solid"
    elif meltingpoint <= 273 and boilingpoint > 273:
        return "liquid"
    else:
        return "gas"
