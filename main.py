"""Entry point for Medabattle Arcade prototype."""

from game.app import MainApp


def main() -> None:
    app = MainApp()
    app.run()


if __name__ == "__main__":
    main()
