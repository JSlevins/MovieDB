from src.cli import CLI

if __name__ == "__main__":
    cli = CLI()
    cli.init_clients()
    cli.init_functions()
    cli.intro_message()
    cli.run_action()