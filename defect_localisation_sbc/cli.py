from defect_localisation_sbc.main import main


def cli():
    """Command line entry point of the application.
    """

    try:
        # Call main
        main()

    except Exception as e:
        # Handle exception here
        pass
