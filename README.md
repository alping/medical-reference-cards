# Medical reference cards
This is an effort to create a series of reference cards, usable to anyone involved in health care and medicine. This is a free and open source project (GNU-GPL), and as such you are at liberty to use the resources here pretty much as you wish (see the LICENCE). However, this is very much a work in progress and no guarantee for the correctness or completeness of these cards can be given. Use these cards at your own risk. With that said, the goal for this project is to provide an accurate, usable, and expandable collection of reference cards. Please feel free to contribute!

## Usage
This is a collection of reference cards for the use in medical practice. These cards are designed to be printed, folded, laminated, and put on a key ring.

The cards can either be downloaded directly from the pdf folder or built from source using the python script `medical-reference-cards.py`

## Instructions for contributors
Contributing is easy! You just need to create one pdf file for the front and one for the back of the card, and then fill in some information in a text file (.yaml). See below for more detailed instructions.

### The building blocks of a card
- Each card has a front and back face.
- Each face has a coloured frame, a heading, a content area, and a footer
- The dimensions of a folded card are 104mm x 165mm
- The dimensions of the content area are 100mm x 140mm
- The meta-data for each card are stored in a .yaml file
- The content for each card is stored in a separate pdf file for each face
- The cards are outputted to a pdf file by running the python script `medical-reference-cards.py`

### Files and naming convention
There are 3 files making up each card (replace `card` with actual card name and `domain` with actual domain name):
+ `domain-card.yaml`
+ `domain-card-front.pdf`
+ `domain-card-back.pdf`

Besides these files, there might be additional source files (files containing data or designs) for each card located in the source subfolder.

For filenames use:
    - The domain and card name as the base
    - All lowercase letters
    - Hyphens (-) to combine words
    - Example filenames for card describing the normal physiology for the pediatrics domain:
        + `pediatrics-normal-physiology.yaml`
        + `pediatrics-normal-physiology_front.pdf`
        + `pediatrics-normal-physiology_back.pdf`

### Structure of .yaml file
```yaml
domain: 'pediatrics'
category: 'general'
header_front: 'Normal Physiology'
header_back: 'Normal Physiology'
# Custom footers are currently not implemented
#footer_front: ''
#footer_back: ''
```
For more info on YAML, see http://yaml.org/

### Dimension of .pdf files
- The dimensions should be 100mm x 140mm (width x height)

## Contributors
Peter - Medical student, Karolinska Institutet, Sweden
