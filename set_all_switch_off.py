from .switch_service import SwitchService

if __name__ == '__main__':
    switch_service = SwitchService()
    switch_service.setup_switches()
    switch_service.set_all_switch_off()
