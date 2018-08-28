#note that the API keys and links have been replaced by placeholders
#I do not want to direct traffic for experimentation to the scraping source, hence the link is not the actual one

#making necessary imports as described

#urllib for retrieval of online hosted docs
import urllib.request

# io for in/out manipulations
import io

#datetime since we want to try various publication dates
import datetime

#system file and path interaction
import os

#uploads to shared location
import dropbox as db


#to define what to convert how (instantiated together)
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter

#the actual converter that takes conversion instruction input as params
from pdfminer.converter import TextConverter

#layout parameters were untouched but are necessary for the converter
from pdfminer.layout import LAParams

#to identify and retrieve all pages of the file
from pdfminer.pdfpage import PDFPage

#the conversion function that shall extract text from a given pdf
def convert_pdf_to_txt(path):
    rsrcmgr = PDFResourceManager()
    retstr = io.StringIO()
    codec = "utf-8"
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    
    #open the passed filepath
    with (open(path, 'rb')) as fp:
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        password = ""
        maxpages = 0
        caching = True
        pagenos = set()
        #iterate through the pages behind the filepath's opened doc
        for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages,password=password,caching=caching,check_extractable=True):
            interpreter.process_page(page)
      
        #retrieve the text from the stream, store in var
        text = retstr.getvalue()
        
        #close the file
        fp.close()
        #delete the file | check whether this step is redundant, see below
        del fp
    device.close()
    retstr.close()
    
    #return the raw text
    return text

#the "scraper", since in our case the publication dates were determining constituents of the URL to the respective document, we can simply go through all desired dates
def grab_hk_journals():
    
    #we need a simple list of dates in the past to try. Although every Friday there is a new issue, it is not guaranteed that only Fridays will yield a positve result (public holidays, other exceptions)
    today = datetime.date.today()
    date_list = [today - datetime.timedelta(days=x) for x in range(0, 1000)]
    
    #our result will be a dict, each key represents an issue and its value will be the text of the publication.
    result_dict = {}
    
    #loop through my date list with the position and the values in mind:
    for index,date in enumerate(date_list):
        
        #our links are in a specific date format
        keydate = date.strftime("%d%m%Y")
        
        try:
            #various print statements to give feedback on where the operation is, and what the problem may be.
            print("now at", keydate)
            
            #constructing the link with the current keydate based on the cms logic of the target
            link = ('___link___/%s/___link___%s.pdf' % (keydate, keydate))
            
            #saving a temp file after retrieval
            temp_pdf = urllib.request.urlretrieve(link, 'temp.pdf')
            
            #passing it to the conversion function
            res = convert_pdf_to_txt(os.path.abspath('temp.pdf'))
            
            #creating the key/value pair for this step
            result_dict[keydate] = res
            
            #give feedback
            print('***SUCCESS***')
                    
        except Exception as e:
            try:
                #the storage convention and domain changed in the history of our docs. hence:
                print(e, "trying to use ipsearch now")
                link = ('___LINK_HERE___' % (keydate, keydate))
                temp_pdf = urllib.request.urlretrieve(link, 'temp.pdf')
                res = convert_pdf_to_txt(os.path.abspath('temp.pdf'))
                result_dict[keydate] = res
                print('***SUCCESS***')
            except:
                #if that all did not work out, please give the error for that date into the result dict for later investigation
                #result_dict[keydate] = e
                print("***no success for this date***")
        finally:
            #show that some step has been completed. (figured that tqdm doesnt give enough indication for in-depth debug)
            print("current date is crawled. proceeding to next")
            
    #remove the temp file after completion
    os.remove('temp.pdf')
    
    return result_dict

#saves the dictionary as a pickle in the desired location as well as somewhere in the cloud
def save_hk_journals_as_dict():
    
    #store the pickle locally
    import pickle
    result = grab_hk_journals()
    save_dict = open('___pickle_name___.pickle','wb')
    pickle.dump(result,save_dict)
    save_dict.close()
    
    #uploading the pickle to shared folder
    print("pickle saved, upload to dropbox now")
    dbx = db.Dropbox("___DB_API_key___") #use own key here
    file_name='___pickle_name___'.pickle'
    dropbox_path='/capstone/get_data/'
    with open(file_name, 'rb') as f:
        dbx.files_upload(f.read(),dropbox_path+file_name,mute=True) #mute is for the upload notification
    os.remove(file_name)
    
    print("file has been saved and uploaded")
    return result

#function call
save_hk_journals_as_dict()
