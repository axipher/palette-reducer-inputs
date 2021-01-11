

# dependencies

import matplotlib.pyplot as pyplot
from PIL import Image

import os
import time
import math
import numpy
import sklearn.cluster
import sklearn.preprocessing
import sys, getopt
import ntpath

tic = time.perf_counter()

def main(argv):
    ### BEGIN CONFIGURATION ###
    
    # Put the EXACT filename you uploaded between the quotes
    # Can be set using '-i <inputfile>' option
    filename = 'photo.jpg'
    
    # The number of colors you want in the final image
    # Can be changed using the '-p <palette-size>' option
    targetColors = 16
    
    # Default output file
    # The output file uses the base file name
    # The Target Colour count can be appended to the filename using the '-a' option
    # The output file will be a PNG
    # Can be set using '-o <outputfile>' option and will be corrected to a PNG
    outfile = ''
    
    # this seed keeps the algorithm deterministic
    # you can change it to a different number if you want
    seed = 0xabad1dea
    
    ### END CONFIGURATION ###
    inputfile = ''
    outputfile = ''
    palettesize = ''
    append = 'false'
    
    print('')
    print('Palette Reducer with inputs!')
    print('By 0xabad1dea and modified by Axipher')
    print('')
    print('')
    
    if not os.path.exists('reduced'):
        os.makedirs('reduced')
    
    try:
        opts, args = getopt.getopt(argv,"hi:o:p:a",["ifile=","ofile=","psize="])
    except getopt.GetoptError:
        print('reduce.py can be used like this:')
        print('reduce.py -i <inputfile> -o <outputfile> -p <palette-size> -a')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print('reduce.py can be used like this:')
            print('reduce.py -i <inputfile> -o <outputfile> -p <palette-size> -a')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
            filename = inputfile
        elif opt in ("-o", "--ofile"):
            outputfile = arg
            outfile = outputfile
        elif opt in ("-p", "--psize"):
            palettesize = arg
            targetColors = int(palettesize)
        elif opt in ("-a", "--append"):
            append = 'true'
    if outfile == '':
        outfile = 'reduced\\' + ntpath.basename(os.path.splitext(filename)[0])
    else:
        outfile = 'reduced\\' + ntpath.basename(os.path.splitext(outputfile)[0])
    if append == 'true':
        outfile = outfile + '-' + str(targetColors)
    outfile = outfile + '.png'
    
    if len(opts) == 0:
        print('Number of opts',len(opts))
        print('')
        print('reduce.py can be used like this:')
        print('reduce.py -i <inputfile> -o <outputfile> -p <palette-size> -a')
        print('')
        print('')
    
    print(f"Input file is '{filename}'")
    print(f"Output file is '{outfile}'")
    print(f"palette size is '{targetColors}'")
    print('')
    
    # massage the file into a consistent colorspace
    # (if one skips the convert("RGB"), some images
    # will work fine and others not at all)
    print('Attempting to load image:')
    print(filename)
    print('')
    
    source = Image.open(filename)
    source = source.convert("RGB")
    source = numpy.asarray(source)
    
    # throw out the alpha channel if present
    # (will screw up the palette reduction otherwise)
    source = source[:,:,:3]
    
    sourcecolors = numpy.unique(source.reshape(-1, source.shape[2]), axis=0)
    # print(sourcecolors)
    print(f"Number of colors in original: {len(sourcecolors)}")
    print('')
    
    # pitch a fit if the image is already below target color count
    assert(len(sourcecolors) >= targetColors)
    
    pyplot.axis("off")
    pyplot.imshow(source, interpolation="none")
    
    # the actual magic 
    # basically, what this does is create n pixel clusters that work like galaxies
    # and at the end, every pixel takes the color at the heart of its own galaxy.
    # this is better than "just take the n most common pixel values" because
    # the cluster galaxies are ~evenly spaced through the colors used, while
    # just taking the n most common can miss large ranges of the color space
    sourceArray = source.reshape(-1, 3)
    simplifier = sklearn.cluster.KMeans(n_clusters=targetColors, random_state=seed).fit(sourceArray)
    simplifiedSource = simplifier.cluster_centers_[simplifier.labels_]
    simplifiedSource = simplifiedSource.reshape(source.shape)
    
    print("Result palette:")
    print(simplifier.cluster_centers_)
    print('')
    
    
    #print("\n\n➡️THIS IS A PREVIEW THUMBNAIL.⬅️\nYOUR RESULT IS IN palette-result.png IN THE FILE BROWSER ON THE LEFT.")
    #print("YOU MAY NEED TO CLICK THE REFRESH-FOLDER ICON TO SEE IT.")
    
    pyplot.axis("off")
    pyplot.imshow(simplifiedSource.astype(numpy.uint8), interpolation="none")
    
    print('Attempting to write new image:')
    print(outfile)
    print('')
    
    pyplot.imsave(fname=outfile, arr=simplifiedSource.astype(numpy.uint8), format='png')
    
    toc = time.perf_counter()
    print(f"Reduced the palette in {toc - tic:0.4f} seconds")
    print('')

if __name__ == "__main__":
   main(sys.argv[1:])
