import click
from peek.image.process import Snapshot
from peek.image.analysis import Annotations

@click.command()
@click.option("--file", "-f", type=str, help="annotation .csv file", default="C:\\Users\\schunckf\\Documents\\Florian\\papers\\nanocosm\\temp\\pics_classic\\20210402\\6_tags.csv")
@click.option("--style", "-s", type=str, help="style of annotations", default="plot_complete_tag_diff")
@click.option("--database", "-d", type=str, help="path to tag database", default="C:\\Users\\schunckf\\Documents\\Florian\\papers\\nanocosm\\results\\image_annotations.csv")
@click.option("--image", "-i", type=str, help="image should normally be provided through annotated file. If necessary it can be provided separately", default=None)
def annotate(file, style, database, image):

    print(f"annotating file {file}")
    # open series and load image

    if image is not None:
        image = Snapshot(path=image)

    a = Annotations(
        path=file,
        image=image,  # image is searched through 
        analysis="undefined",  # analysis should be provided by annotation file
        tag_db_path=database,
    )

    a.start(plot_type=style)
    
    print("completed.")        


if __name__ == "__main__":
    annotate()