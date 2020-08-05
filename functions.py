"""
This file contains various functions used in the main
counting notebook.
"""

import matplotlib.pyplot as plt
import numpy as np
from skimage import exposure, feature, filters, io, morphology
from ipywidgets import widgets, interactive, fixed
from math import sqrt
from collections import Counter
import xml.etree.ElementTree as ET
from xml.dom import minidom

def load_and_get_name_of_image(path,
                               channel=1,
                               cmap='jet',
                               show_image=True
                              ):
    """
    Loads an image, strips out the desired channel,
    and optionally displays the image.
    
    Returns image and its file name stem for later
    use.
    """
    
    if not path:
        path = 'Drd2_Adult_S_conf_25X_CPU1_cryo_NAV.jpg'
    
    stem = path.split('.')[0]
    rawpic = io.imread(path)
    img = rawpic[:,:, channel]
    
    if show_image:
        io.imshow(img, cmap=cmap)
    
    return img, stem


def adjust_image(image,
                 lower_thresh=2, upper_thresh=98,
                 filter_size=0, 
                 cmap='jet'
                ):
    """
    Applies contrast stretching to an image, then
    uses a white top-hat filter to remove small patches
    of brightness that would cause false positives later.
    
    Input: image; values for min and max percentile
    brightnesses to keep; size below which bright patches
    will be removed; colourmap.
    
    Output: image, hopefully with most of the background stripped
    out. If it's worked well, it'll look like bright blobs on a
    dark background.
    """
    
    p2, p98 = np.percentile(image, (lower_thresh, upper_thresh))
    img_rescale = exposure.rescale_intensity(img, in_range=(p2, p98))
    selem = morphology.disk(filter_size)
    wht_tophat = morphology.white_tophat(img_rescale,selem=selem)
    io.imshow(img_rescale - wht_tophat, cmap=cmap)
    
    return img_rescale

def detect_blobs(original_image,
                 processed_image,
                 max_sigma=30,
                 threshold=0.1
                ):
    """
    Detects bright blobs in an image using the scikit-image
    determinant of gaussian technique, then marks them on the
    image.
    
    Input: original and processed images; max_sigma to determine 
    upper limit for blob size; threshold to determine how bright
    something needs to be before it's identified as a blob.
    
    Output: displays image with red rings around detected blobs;
    returns array of blob markers (y,x,radius).
    """
    
    blobs_dog = feature.blob_dog(processed_image,
                                 max_sigma=sigma,
                                 threshold=threshold
                                )
    blobs_dog[:, 2] = blobs_dog[:, 2] * sqrt(2) #radius calcs
    fig,axes = plt.subplots(ncols=3, figsize=(16,12))
    ax_im_pairs = list(zip(axes,
                           (original_image,
                            processed_image,
                            original_image),
                           (False,True,True)
                          ))
    for ax,im,draw in ax_im_pairs:
        ax.imshow(im)
        if draw == True:
            for blob in blobs_dog:
                y,x,r = blob
                c = plt.Circle((x, y), r,
                               color='r',
                               linewidth=2,
                               fill=False
                              )
                ax.add_patch(c)
    print("{} blobs detected.".format(len(blobs_dog)))
    
    return blobs_dog

def save_for_imagej(coords, filestem):
    """
    Dumps out the blob coordinates as an XML file suitable for
    use in the ImageJ cell counter plugin. If the file name isn't
    a perfect match with the one you pass to this function, the
    cell counter plugin will throw an error and not work. It's a 
    really fragile safety check and ought to be bypassable, but
    the plugin hasn't been updated for ten years soo......
    
    Inputs: coordinates array from the detect_blobs function; file
    name stem from load_and_get_name_of_image function.
    
    Output: saves an XML file for use in ImageJ. All markers will
    be saved as marker type 1 for simplicity.
    """
    
    def prettify(elem):
        """
        Return a pretty-printed XML string for the element.
        From https://gist.github.com/jefftriplett/3980637
        """
        rough_string = ET.tostring(elem, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ", encoding="UTF-8").decode('UTF8')
    
    marker_types = list(range(1,9))
    marks_to_store = {1: coords}

    root = ET.Element("CellCounter_Marker_File")
    imgprops = ET.SubElement(root, "Image_Properties")
    imgfname = ET.SubElement(imgprops, "Image_Filename")
    imgfname.text = filestem
    markerdata = ET.SubElement(root, "Marker_Data")
    curtype = ET.SubElement(markerdata, "Current_Type")
    curtype.text = '0'
    for i in marker_types:
        marks_container = ET.SubElement(markerdata, "Marker_Type")
        mtype = ET.SubElement(marks_container, "Type")
        mtype.text = str(i)
        if i in marks_to_store.keys():
            for y,x in marks_to_store[i]:
                mark = ET.SubElement(mtype, "Marker")
                markx = ET.SubElement(mark, "MarkerX")
                markx.text = str(int(x))
                marky = ET.SubElement(mark, "MarkerY")
                marky.text = str(int(y))
                markz = ET.SubElement(mark, "MarkerZ")
                markz.text = str(int(1))

    with open('{}.xml'.format(filestem, 'w') as f:
        f.write(prettify(root))