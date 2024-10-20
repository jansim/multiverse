import argparse
from pathlib import Path
from typing import Union

from .multiverse import DEFAULT_SEED, MultiverseAnalysis

def run_cli(dimensions: Union[Path, dict, None] = None) -> None:
    """Run a multiverse analysis from the command line.

    Args:
        dimensions (Union[Path, dict, None], optional): Manually specify
            dimensions. Set to None to use normal default / allow specification
            as an argument. Defaults to None.

    Raises:
        FileNotFoundError: If the dimensions file is not found.
        NotADirectoryError: If the output directory is not found.
    """
    parser = argparse.ArgumentParser("multiversum")

    parser.add_argument(
        "--mode",
        help=(
            "How to run the multiverse analysis. "
            "(continue: continue from previous run, "
            "full: run all universes, "
            "test: run only a small subset of universes)"
        ),
        choices=["full", "continue", "test"],
        default="full",
    )

    def verify_file(string):
        if Path(string).is_file():
            return string
        else:
            raise FileNotFoundError(string)
    if dimensions is None:
        parser.add_argument(
            "--dimensions",
            help=(
                "Relative path to a JSON file with a dictionary of dimensions for the multiverse."
            ),
            default="multiverse.json",
            type=verify_file,
        )

    parser.add_argument(
        "--notebook",
        help=(
            "Relative path to the notebook to run."
        ),
        default="./universe-analysis.ipynb",
        type=verify_file,
    )

    def verify_dir(string):
        if Path(string).is_dir():
            return string
        else:
            raise NotADirectoryError(string)
    parser.add_argument(
        "--output-dir",
        help=(
            "Relative path to output directory for the results."
        ),
        default="./output_dir",
        type=verify_dir,
    )

    parser.add_argument(
        "--seed",
        help=(
            "The seed to use for the analysis."
        ),
        default=str(DEFAULT_SEED),
        type=int,
    )
    args = parser.parse_args()

    multiverse_analysis = MultiverseAnalysis(
        dimensions=Path(args.dimensions) if dimensions is None else dimensions,
        notebook=Path(args.notebook),
        output_dir=Path(args.output_dir),
        new_run=(args.mode != "continue"),
        seed=args.seed,
    )

    multiverse_grid = multiverse_analysis.generate_grid(save=True)
    print(f"Generated N = {len(multiverse_grid)} universes")

    print(f"~ Starting Run No. {multiverse_analysis.run_no} (Seed: {multiverse_analysis.seed})~")

    # Run the analysis for the first universe
    if args.mode == "test":
        print("Small-Scale-Test Run")
        multiverse_analysis.visit_universe(multiverse_grid[0])
        if len(multiverse_grid) > 1:
            multiverse_analysis.visit_universe(multiverse_grid[len(multiverse_grid) - 1])
    elif args.mode == "continue":
        print("Continuing Previous Run")
        missing_universes = multiverse_analysis.check_missing_universes()[
            "missing_universes"
        ]

        # Run analysis only for missing universes
        multiverse_analysis.examine_multiverse(multiverse_grid=missing_universes)
    else:
        print("Full Run")
        # Run analysis for all universes
        multiverse_analysis.examine_multiverse(multiverse_grid=multiverse_grid)

    multiverse_analysis.aggregate_data(save=True)

    multiverse_analysis.check_missing_universes()
