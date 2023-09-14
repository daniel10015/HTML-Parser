# HTML-Parser
Custom HTML parser for SpongeBob episode transcripts for every SpongeBob episode. There's a character variable ,`CHARACTER`, in the source that you can modify for it to grab lines of other SpongeBob characters. 

I haven't tried this, but maybe it can work for other content on the same website if you prompt with correct episode name??? 
## Pre reqs
- Python
- dependencies:
  - time (you can delete this if you don't want to time it)
    - pip install time
  - requests (used for http requests)
    - pip install requests
  - multiprocessing (paralle processing for the parsing, cut time down by number of cores available (ie 80 seconds to 10 seconds)

## Usage
- Python3 won't work with requests (at least the one im using)
  - print lines to stdout
    - `python scape.py`
  - redirect stdout to a file
    - `python scape.py >> file.txt`
   
# IMPORTANT NOTES
- There's no uppercase words in the dialogue, there's only **bolded words in the dialogue** which implies that it means it's supposed to be when the character raises their voice, yell, etc. I purposely **left the HTML for bolded words that are dialogue in the standard output.**
- What this means is every single piece of dialogue will be extracted, however, instead of capitalizing the bolded parts, I **left it in just in case there's another interpretation.**
- So.. either add in a few extra lines during parsing to change it to uppercase, or whatever you want to change it into. I haven't written the code yet, but when I do I'll push the update here and update this section

## Misc
- I didn't write this to be the most maintainable. I tried my best for obvious cases like parsing, processes, passing variable inputs (ie http request URLs), etc, but my **main goal is to get the job done quickly** so I didn't boilerplate as much code as I would for a more crucial program. After all this is just for getting data, it's step 0 for me, so I don't want to spend too many hours on this. 
  - On that note, if you can't understand anything, shoot me a DM on discord, because I haven't seen ANY parsers for these and I think it's super useful.   
