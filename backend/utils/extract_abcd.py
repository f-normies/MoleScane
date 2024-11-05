import numpy as np
import os
import glob
import pandas as pd
from skimage import io, exposure, morphology, filters, color, segmentation, feature, measure, img_as_float, img_as_ubyte
from skimage.segmentation import watershed
from skimage.color.adapt_rgb import adapt_rgb, each_channel, hsv_value
from scipy import ndimage as ndi
from tqdm import tqdm
import multiprocessing

# Constants
structuring_element = morphology.disk(7)
attr = [
        'ImgName', 
        'AsymIdx', 
        'Eccentricity', 
        'CI', 
        'StdR', 
        'StdG', 
        'StdB', 
        'Diameter', 
        'Correlation', 
        'Homogeneity', 
        'Energy', 
        'Contrast'
    ]

# Helper functions
@adapt_rgb(each_channel)
def morph_closing_each(image, struct_element):
    return morphology.closing(image, struct_element)


@adapt_rgb(hsv_value)
def morph_closing_hsv(image, struct_element):
    return morphology.closing(image, struct_element)

@adapt_rgb(each_channel)
def median_filter_each(image, struct_element):
    return filters.median(image, struct_element)


@adapt_rgb(hsv_value)
def median_filter_hsv(image, struct_element):
    return filters.median(image, struct_element)

def process_image(image_input):
    try:
        if isinstance(image_input, str):
            image = io.imread(image_input)
        elif isinstance(image_input, np.ndarray):
            image = image_input

        # Preprocessing
        equalized_adapthist = exposure.equalize_adapthist(image)
        img_morph_closing = morph_closing_each(equalized_adapthist, structuring_element)
        img_filtered = median_filter_each(img_morph_closing, structuring_element)

        # Segmentation
        gray_img = color.rgb2gray(img_filtered)

        elevation_map = filters.sobel(gray_img)
        elevation_map = elevation_map.astype(np.float32)

        markers = np.zeros_like(gray_img)
        threshold = filters.threshold_isodata(gray_img)
        markers[gray_img > threshold] = 1
        markers[gray_img < threshold] = 2
        markers = markers.astype(int)

        segmented_img = segmentation.watershed(elevation_map, markers)
        segmented_img = ndi.binary_fill_holes(segmented_img - 1)
        segmented_img = morphology.remove_small_objects(segmented_img, min_size=800)
        img_border_cleared = segmentation.clear_border(segmented_img)

        labeled_img = morphology.label(img_border_cleared)

        props = measure.regionprops(labeled_img)

        num_labels = len(props)
        areas = [region.area for region in props]

        if num_labels > 0 and areas[np.argmax(areas)] >= 1200:
            target_label = props[np.argmax(areas)].label
        else:
            labeled_img = morphology.label(segmented_img)
            props = measure.regionprops(labeled_img)
            areas = [region.area for region in props]

            extents = [region.extent for region in props]

            region_max1 = np.argmax(areas)
            if len(props) > 1:
                areas_copy = areas.copy()
                areas_copy[region_max1] = 0
                region_max2 = np.argmax(areas_copy)
            if len(props) > 2:
                areas_copy[region_max2] = 0
                region_max3 = np.argmax(areas_copy)

            if extents[region_max1] > 0.50:
                target_label = props[region_max1].label
            elif len(props) > 1 and extents[region_max2] > 0.50:
                target_label = props[region_max2].label
            elif len(props) > 2 and extents[region_max3] > 0.50:
                target_label = props[region_max3].label
            else:
                target_label = props[region_max1].label

        lesion_region = props[target_label - 1]

        # ABCD features extraction
        ## ASSYMETRY
        area_total = lesion_region.area
        img_mask = lesion_region.image

        horizontal_flip = np.fliplr(img_mask)
        diff_horizontal = img_mask * ~horizontal_flip

        vertical_flip = np.flipud(img_mask)
        diff_vertical = img_mask * ~vertical_flip

        diff_horizontal_area = np.count_nonzero(diff_horizontal)
        diff_vertical_area = np.count_nonzero(diff_vertical)
        asymm_idx = 0.5 * ((diff_horizontal_area / area_total) + (diff_vertical_area / area_total))
        ecc = lesion_region.eccentricity

        ## BORDER
        compact_index = (lesion_region.perimeter ** 2) / (4 * np.pi * area_total)

        ## COLOR
        sliced = image[lesion_region.slice]
        lesion_r = sliced[:, :, 0]
        lesion_g = sliced[:, :, 1]
        lesion_b = sliced[:, :, 2]

        C_r = np.std(lesion_r) / np.max(lesion_r)
        C_g = np.std(lesion_g) / np.max(lesion_g)
        C_b = np.std(lesion_b) / np.max(lesion_b)

        ## DIAMETER
        eq_diameter = lesion_region.equivalent_diameter

        ## TEXTURE
        glcm = feature.graycomatrix(image=img_as_ubyte(gray_img), distances=[1],
                                angles=[0, np.pi/4, np.pi/2, np.pi * 3/2],
                                symmetric=True, normed=True)

        correlation = np.mean(feature.graycoprops(glcm, prop='correlation'))
        homogeneity = np.mean(feature.graycoprops(glcm, prop='homogeneity'))
        energy = np.mean(feature.graycoprops(glcm, prop='energy'))
        contrast = np.mean(feature.graycoprops(glcm, prop='contrast'))

        features = [
            image_path.split('/')[-1],
            asymm_idx,
            ecc,
            compact_index,
            C_r,
            C_g,
            C_b,
            eq_diameter,
            correlation,
            homogeneity,
            energy,
            contrast
        ]

        return features
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return [os.path.basename(image_path)] + [np.nan]*11

def extract_abcd(images_path):
    supported_extensions = ('.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp')

    image_paths = [
        os.path.join(images_path, filename)
        for filename in os.listdir(images_path)
        if filename.lower().endswith(supported_extensions)
    ]

    num_processes = 32
    with multiprocessing.Pool(processes=num_processes) as pool:
        results = list(tqdm(pool.imap(process_image, image_paths), total=len(image_paths)))

    img_df = pd.DataFrame(data=results, columns=attr)
    return img_df


if __name__=='__main__':
    images_path = '.'

    img_df = extract_abcd(images_path)
    img_df.to_csv('abcd.csv', index=False)
    print(img_df)