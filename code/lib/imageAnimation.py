import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PIL import Image
import os
import configurePaths as configurePaths

cProjectRoot = configurePaths.getProjectRoot()
_, _, _, _, _, _, cFiguresOutputPath = configurePaths.getSubfolderPaths(cProjectRoot)

## load all images with .png from a folder
def loadImages(folder, fileNamePrefix):
    images = []
    fileNames = os.listdir(folder)
    # sort the file names based on the year
    sortedFileNames = sorted(fileNames)
    for filename in sortedFileNames:
        if filename.startswith(fileNamePrefix) and not filename.endswith("Animated.gif"):
            img = Image.open(os.path.join(folder, filename))
            images.append(img)
    return images

# animate images in the image_list with interval delay (default 500 ms)
def animateImages(image_list, animatedFileFullPath, interval=500):
    fig, ax = plt.subplots()
    #fig.patch.set_facecolor((0, 0, 0, 0))  # Set the background to transparent
    ax.set_axis_off()  # Remove axes

    img_display = ax.imshow(image_list[0])

    def update(i):
        img_display.set_data(image_list[i % len(image_list)])
        return img_display,

    ani = animation.FuncAnimation(fig, update, frames=len(image_list), interval=interval, blit=True, repeat=False)

    # Save the animation as a GIF
    ani.save(animatedFileFullPath, writer='pillow')

# load all images (ending with .PNG) from a folder and animate
def animateImagesFromFolder(imageFolder, fileNamePrefix, animatedFileFullPath, interval):
    image_sequence = loadImages(imageFolder, fileNamePrefix)
    if image_sequence:
        animateImages(image_sequence, animatedFileFullPath, interval)
    else:
        print(f"No images found in the folder: {imageFolder}")

if __name__ == "__main__":
    fileNamePrefix = "cleanRentIncomeRatioScatter"
    animatedFileFullPath = configurePaths.getFilePath(cFiguresOutputPath, f"{fileNamePrefix}-Animated.gif")
    animateImagesFromFolder(cFiguresOutputPath, fileNamePrefix, animatedFileFullPath, 1000)

