from knapsack2d.ui.main_window import MainWindow


def run() -> int:
    from knapsack2d.ui.app import run as app_run

    return app_run()


__all__ = ["MainWindow", "run"]
