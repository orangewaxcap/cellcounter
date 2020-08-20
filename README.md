# cellcounter
A human-in-the-loop tool to identify cells in microscope images. Cell coordinates can be downloaded as an XML file compatible with ImageJ's CellCounter plugin.

To use the tool:

### Load an image
1. Run the tool in JupyterLab or a Jupyter notebook.
2. Upload an image using the "Upload File" button.
3. Select the desired image channel (1: red, 2: green, 3: blue)

The uploaded image is presented in three forms. Left to right: background removed; background removed and cell markers added; original image with cell markers added.
### Remove the background
4. Adjust the contrast thresholds until the left image shows clear blobs and a clear background. Typical settings for the lower and upper thresholds are 85 and 95 respectively.
5. If the background is particularly noisy, try adjusting the filter size slider to remove background clutter. Small values work best.
### Tweak blob detection settings
Bright blobs that could be cells are marked with red circles. Note that the centre and right images won't reflect new contrast settings until either the max sigma or threshold sliders are tweaked.

6. Adjust the max sigma slider until the cell markers are no larger than an individual cell.

7. Adjust the threshold slider until as many cells as possible are marked, with as few false positives from background noise. Higher threshold values mean dimmer blobs are ignored.
### Export the image
8. Click the prep file for download button.
9. Click the download ImageJ file button.

A test image and an example output file are available in this repo. The test image is sourced from http://www.gensat.org/imagenavigator.jsp?imageID=50657. 
