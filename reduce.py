

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


def main(argv):
    tic = time.perf_counter()
    
    # Waifu2x-caffe available from: https://github.com/lltcggie/waifu2x-caffe/releases
    waifuPath = "C:\Programs\waifu2x-caffe\waifu2x-caffe-cui.exe"
    waifuOptionsPre = '-i '
    waifuOptionsMid = ' -o '
    waifuOptionsPost = ' -p cpu -s 2.0'
    
    # OptiPNG available from: http://optipng.sourceforge.net/
    optiPNGPath = "C:\Programs\optipng-0.7.7-win32\optipng.exe"
    optiPNGOptionsPre = ''
    optiPNGOptionsMid = ' -out '
    optiPNGOptionsPost = ' -clobber'
    
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
    
    if not os.path.exists('reduced\\' + str(targetColors)):
        os.makedirs('reduced\\' + str(targetColors))
    
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
        outfile = 'reduced\\' + str(targetColors) + '\\' + ntpath.basename(os.path.splitext(filename)[0])
    else:
        outfile = 'reduced\\' + str(targetColors) + '\\' + ntpath.basename(os.path.splitext(outputfile)[0])
    if append == 'true':
        outfile = outfile + '-' + str(targetColors)
    outfileWaifu = outfile + '_waifu2x.png'
    outfileoptiPNG = outfile + '_optiPNG.png'
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
    
    im = Image.open(filename)
    
    # Provide the target width and height of the image and resize it 50%
    (width, height) = (im.width, im.height)
    (width_5, height_5) = (width // 2, height // 2)
    source = im.resize((width_5, height_5))
    (width2, height2) = (source.width, source.height)
    
    print(f"Source dimensions: {width}x{height}")
    print(f"Source halved dimensions: {width2}x{height2}")
    
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
    # pyplot.imshow(source, interpolation="none")
    
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
    
    #print("Result palette:")
    #print(simplifier.cluster_centers_)
    #print('')
    
    
    #print("\n\n➡️THIS IS A PREVIEW THUMBNAIL.⬅️\nYOUR RESULT IS IN palette-result.png IN THE FILE BROWSER ON THE LEFT.")
    #print("YOU MAY NEED TO CLICK THE REFRESH-FOLDER ICON TO SEE IT.")
    
    pyplot.axis("off")
    # pyplot.imshow(simplifiedSource.astype(numpy.uint8), interpolation="none")
    
    print('Attempting to write new image:')
    print(outfile)
    print('')
    
    pyplot.imsave(fname=outfile, arr=simplifiedSource.astype(numpy.uint8), format='png')
    
    toc = time.perf_counter()
    print(f"Reduced the palette in {toc - tic:0.4f} seconds")
    print('')
    tic = time.perf_counter()
    
    print("Attempting Waifu2x-caffe transformation with 2x scale")
    waifuOptions = waifuOptionsPre + outfile + waifuOptionsMid + outfileWaifu + waifuOptionsPost
    print(f"Command: {waifuPath}")
    print(f"Options: {waifuOptions}")
    os.system(waifuPath + " " + waifuOptions)
    
    toc = time.perf_counter()
    print(f"Ran through Waifu2x-caffe in {toc - tic:0.4f} seconds")
    print('')
    
    print("Attempting optiPNG processing")
    optiPNGOptions = optiPNGOptionsPre + outfileWaifu + optiPNGOptionsMid + outfileoptiPNG + optiPNGOptionsPost
    print(f"Command: {optiPNGPath}")
    print(f"Options: {optiPNGOptions}")
    os.system(optiPNGPath + " " + optiPNGOptions)
    
    toc = time.perf_counter()
    print(f"Ran through OptiPNG in {toc - tic:0.4f} seconds")
    print('')
    
    # Provide the target width and height of the final image
    imFinal = Image.open(filename)
    (widthFinal, heightFinal) = (imFinal.width, imFinal.height)
    print(f"Final Image: {outfileoptiPNG}")
    print(f"Source dimensions: {widthFinal}x{heightFinal}")

if __name__ == "__main__":
   main(sys.argv[1:])
