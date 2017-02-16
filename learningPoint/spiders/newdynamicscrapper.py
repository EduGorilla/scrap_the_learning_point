import csv
import scrapy
from bs4 import BeautifulSoup
from pathlib import Path
import logging


class QuotesSpider(scrapy.Spider):
    name = "newdynamicscrapper"

    #  start_urls=['http://www.thelearningpoint.net/home/school-listings/cbse-13/Bayonet-School-Bayonet-School-C-O-Infantry-School--Mhow-1030454']

    def start_requests(self):
        base_url = 'http://www.thelearningpoint.net/system/app/pages/search?scope=search-site&q=school&offset='

        print "Scraping Started for "+base_url+". Please wait..."

        for counter in xrange(0, 57174):
            url = base_url + str(counter)
            #print "Url to be scrapped : "+url
            yield scrapy.Request(url=url, callback=self.parse_page)

    def parse_page(self, response):
        try:
            page = (response.xpath('//td[@id="col0"]').css('div.sites-search-result h3 a::attr(href)').extract_first())
            link = response.urljoin(page)
            yield scrapy.Request(url=link, callback=self.parse_school)
        except:
            print "could not go to indivitual school"
        

    def parse_school(self, response):
        print "Scrapping school data: ", response;
        dataToScrap = ['Name of Institution', 'Affiliation Number', 'State', 'District', 'locality',
                      'Postal Address', 'Pin Code', 'STD', 'Phone Office 1', 'Phone Office 2', 'Phone Residence 1',
                      'Phone Residence 2', 'FAX No', 'Email', 'Website', 'Year of Foundation',
                      'Date of First Openning of School', 'Name of Principal/ Head of Institution', 'Sex',
                      'Principal Education/Professional Qualifications', 'Number of Experience Years',
                      'Administrative', 'Teaching', 'Status of The School', 'Type of affiliation',
                      'Affiliation Period From', 'Affiliation Period To',
                      'Name of Trust/ Society/ Managing Committee', 'extra'];
        try:
            data = {}
            data['Name of Institution'] = unicode('')
            data['Affiliation Number'] = unicode('')
            data['State'] = unicode('')
            data['District'] = unicode('')
            data['Postal Address'] = unicode('')
            data['Pin Code'] = unicode('')
            data['STD'] = unicode('')
            data['Phone Office 1'] = unicode('')
            data['Phone Office 2'] = unicode('')
            data['Phone Residence 1'] = unicode('')
            data['Phone Residence 2'] = unicode('')
            data['FAX No'] = unicode('')
            data['Email'] = unicode('')
            data['Website'] = unicode('')
            data['Year of Foundation'] = unicode('')
            data['Date of First Openning of School'] = unicode('')
            data['Name of Principal/ Head of Institution'] = unicode('')
            data['Sex'] = unicode('')
            data['Principal Education/Professional Qualifications'] = unicode('')
            data['Number of Experience Years'] = unicode('')
            data['Administrative'] = unicode('')
            data['Teaching'] = unicode('')
            data['Status of The School'] = unicode('')
            data['Type of affiliation'] = unicode('')
            data['Affiliation Period From'] = unicode('')
            data['Affiliation Period To'] = unicode('')
            data['Name of Trust/ Society/ Managing Committee'] = unicode('')
            data['locality'] = unicode('')
            data['extra'] = unicode('')

            point = 0
            page = BeautifulSoup(response.css('body').extract()[0], 'html.parser').find_all('td')

            try:
                for val, i in enumerate(page):
                    if i.b is not None and i.b.string is not None and i.b.string.strip() == unicode('Name of Institution'):
                        data['Name of Institution'] = page[val + 1].string.strip();
            except Exception as e:
                print "Name not found : "+str(e);

            try:
                for val, i in enumerate(page):
                    if i.b is not None and i.b.string is not None and i.b.string.strip() == unicode('Affiliation Number'):
                        data['Affiliation Number'] = page[val + 1].string.strip();
            except Exception as e:
                print "Affiliation not found : "+str(e);

            try:
                for val, i in enumerate(page):
                    if i.b is not None and i.b.string is not None and i.b.string.strip() == unicode('State'):
                        data['State'] = page[val + 1].string.strip();
            except Exception as e:
                print "State not found : "+str(e);

            try:
                for val, i in enumerate(page):
                    if i.b is not None and i.b.string is not None and i.b.string.strip() == unicode('District'):
                        data['District'] = page[val + 1].string.strip();
            except Exception as e:
                print "District not found : "+str(e);

            try:
                for val, i in enumerate(page):
                    if i.b is not None and i.b.string is not None and i.b.string.strip() == unicode('Phone No. with STD Code'):
                        data['Phone No. with STD Code'] = page[val + 1].string.strip();
            except Exception as e:
                print "Phone No not found : "+str(e);

            try:
                for val, i in enumerate(page):
                    if i.b is not None and i.b.string is not None and i.b.string.strip() == unicode('Postal Address'):
                        data['Postal Address'] = page[val + 1].string.strip();
            except Exception as e:
                print "Postal Address : "+str(e);

            try:
                for val, i in enumerate(page):
                    if i.b is not None and i.b.string is not None and i.b.string.strip().lower().find('pin') is not -1:
                        data['Pin Code'] = page[val + 1].string.strip();
            except Exception as e:
                print "Pin Code not found : "+str(e);

            try:
                for val, i in enumerate(page):
                    if i.b is not None and i.b.string is not None and i.b.string.strip().find('Office') is not -1:
                        # data['Phone Office 1'] = page[val+1].string.strip()
                        point = val;
            except Exception as e:
                print "Office found : "+str(e);

            try:
                phoneNumber1 = data['STD'] + page[point + 1].string.strip();
                data['Phone Office 1'] = ''.join(filter(str.isdigit, phoneNumber1));
            except:
                #print "Phone Office 1 not found"
                data['Phone Office 1'] = unicode('')
            try:
                data['Phone Office 2'] = data['STD'] + page[point + 2].string.strip();
            except:
                #print "Phone Office 2 not found"
                data['Phone Office 2'] = unicode('')
            try:
                data['Phone Residence 1'] = data['STD'] + page[point + 4].string.strip();
            except:
                #print "Phone Residence 1 not found"
                data['Phone Residence 1'] = unicode('')
            try:
                data['Phone Residence 2'] = data['STD'] + page[point + 5].string.strip();
            except:
                #print "Phone Residence 2 not found"
                data['Phone Residence 2'] = unicode('')

            try:
                for val, i in enumerate(page):
                    if i.b is not None and i.b.string is not None and i.b.string.strip().find('FAX No') is not -1:
                        data['FAX No'] = page[val + 1].string.strip()
            except:
                data['FAX No'] = unicode('')

            try:
                for val, i in enumerate(page):
                    if i.b is not None and i.b.string is not None and i.b.string.strip().find('Email') is not -1:
                        data['Email'] = page[val + 1].string.strip()
            except:
                data['Email'] = unicode('')

            try:
                for val, i in enumerate(page):
                    if i.b is not None and i.b.string is not None and i.b.string.strip().find('Website') is not -1:
                        data['Website'] = page[val + 1].string.strip()
            except:
                data['Website'] = unicode('')
                
            try:
                for val, i in enumerate(page):
                    if i.b is not None and i.b.string is not None and i.b.string.strip().find('Year of Foundation') is not -1:
                        data['Year of Foundation'] = page[val + 1].string.strip()
            except:
                data['Year of Foundation'] = unicode('')

            try:
                for val, i in enumerate(page):
                    if i.b is not None and i.b.string is not None and i.b.string.strip().find('Openning') is not -1:
                        data['Date of First Openning of School'] = page[val + 1].string.strip()
            except:
                data['Date of First Openning of School'] = unicode('')

            try:
                for val, i in enumerate(page):
                    if i.b is not None and i.b.string is not None and i.b.string.strip().find('Head') is not -1:
                        data['Name of Principal/ Head of Institution'] = page[val + 1].string.strip()
            except:
                data['Name of Principal/ Head of Institution'] = unicode('')

            try:
                for val, i in enumerate(page):
                    if i.b is not None and i.b.string is not None and i.b.string.strip() == 'Sex':
                        data['Sex'] = page[val + 1].string.strip()
            except:
                data['Sex'] = unicode('')


            try:
                for val, i in enumerate(page):
                    if i.b is not None and i.b.string is not None and i.b.string.strip().find('Qualifications') is not -1:
                        data['Principal Education/Professional Qualification'] = page[val + 1].string.strip()
            except:
                data['Principal Education/Professional Qualification'] = unicode('')

            try:
                for val, i in enumerate(page):
                    if i.b is not None and i.b.string is not None and i.b.string.strip().find('Experience') is not -1:
                        data['Number of Experience Years'] = page[val + 1].string.strip()
            except:
                data['Number of Experience Years'] = unicode('')

            try:
                for val, i in enumerate(page):
                    if i.b is not None and i.b.string is not None and i.b.string.strip().find('Administrative') is not -1:
                        data['Administrative'] = page[val + 1].string.strip()
            except:
                data['Administrative'] = unicode('')

            try:
                for val, i in enumerate(page):
                    if i.b is not None and i.b.string is not None and i.b.string.strip().find('Teaching') is not -1:
                    	data['Teaching'] = page[val + 1].string.strip()
            except:
                data['Teaching'] = unicode('')

            try:
                for val, i in enumerate(page):
                    if i.b is not None and i.b.string is not None and i.b.string.strip().find(
                            'Status of The School') is not -1:
                        data['Status of The School'] = page[val + 1].string.strip()
            except:
                data['Status of The School'] = unicode('')

            try:
                for val, i in enumerate(page):
                    if i.b is not None and i.b.string is not None and i.b.string.strip().find(
                            'Type of affiliation') is not -1:
                        data['Type of affiliation'] = page[val + 1].string.strip()
            except:
                data['Type of affiliation'] = unicode('')

            try:
                for val, i in enumerate(page):
                    if i.b is not None and i.b.string is not None and i.b.string.strip().find(
                            'Affiliation Period From') is not -1:
                        data['Affiliation Period From'] = page[val + 1].string.strip()
            except:
                data['Affiliation Period From'] = unicode('')

            try:
                for val, i in enumerate(page):
                    if i.b is not None and i.b.string is not None and i.b.string.strip().find('Affiliation Period To') is not -1:
                        data['Affiliation Period To'] = page[val + 1].string.strip()
            except:
                data['Affiliation Peroid To'] = unicode('')

            try:
                for val, i in enumerate(page):
                    if i.b is not None and i.b.string is not None and i.b.string.strip().find('Trust') is not -1:
                        data['Name of Trust/ Society/ Managing Committee'] = page[val + 1].string.strip()
            except:
                data['Name of Trust/ Society/ Managing Committee'] = unicode('')

            try:
                for val, i in enumerate(page):
                    if i.b is not None and i.b.string is not None and i.b.string.strip().find('Police') is not -1:
                        data['locality'] = page[val + 1].string.strip()
            except:
                data['locality'] = unicode('')

            #print "Showing data: ", data

            if (data['Name of Institution']==unicode('') and data['Affiliation Number']==unicode('') and data['State']==unicode('') and data['District']==unicode('') and data['locality']==unicode('') and data['Postal Address']==unicode('') and data['Pin Code']==unicode('') and data['STD']==unicode('') and data['Phone Office 1']==unicode('') and data['Phone Office 2']==unicode('') and data['Phone Residence 1']==unicode('') and data['Phone Residence 2']==unicode('') and data['FAX No']==unicode('') and data['Email']==unicode('') and data['Website']==unicode('') and data['Year of Foundation']==unicode('') and data['Date of First Openning of School']==unicode('') and data['Name of Principal/ Head of Institution']==unicode('') and data['Sex']==unicode('') and data['Principal Education/Professional Qualifications']==unicode('') and data['Number of Experience Years']==unicode('') and data['Administrative']==unicode('') and data['Teaching']==unicode('') and data['Status of The School']==unicode('') and data['Type of affiliation']==unicode('') and data['Affiliation Period From']==unicode('') and data['Affiliation Period To']==unicode('') and data['Name of Trust/ Society/ Managing Committee']==unicode('') and data['extra']==unicode('')):
                
                
                with open("new_partial_missed.csv","a") as total_failed:
                    fieldnames = ['links']
                    writer = csv.DictWriter(total_failed,fieldnames=fieldnames)
                    writer.writerow({'links' : response})
            

            check = Path("output/" + data['State'].lower() + ".csv")
            fieldnames = ['Name', 'Affiliation Number', 'State', 'City', 'Locality', 'Country',
                          'Postal Address', 'PinCode', 'Phone1', 'Phone2', 'Phone3', 'Phone4', 'Phone5',
                          'Images URL', 'Working Hours', 'Details', 'Services Offered',
                          'FAX No', 'Mail', 'Website', 'Year of Foundation',
                          'Date of First Openning of School', 'Name of Principal/ Head of Institution', 'Sex',
                          'Principal Education/Professional Qualifications', 'Number of Experience Years',
                          'Administrative', 'Teaching', 'Status of The School', 'Type of affiliation',
                          'Affiliation Period From', 'Affiliation Period To',
                          'Name of Trust/ Society/ Managing Committee', 'extra'];
            if not check.is_file():
                with open("new_output/" + data['State'].lower() + ".csv", "wb") as myFile:
                    writer = csv.DictWriter(myFile, fieldnames=fieldnames)
                    writer.writeheader()

            with open("new_output/" + data['State'].lower() + ".csv", "a") as myFile:
                writer = csv.DictWriter(myFile, fieldnames=fieldnames)

                writer.writerow({
                    'Name': data['Name of Institution'],
                    'Affiliation Number': data['Affiliation Number'],
                    'State': data['State'],
                    'City': data['District'],
                    'Locality': data['locality'],
                    'Country': 'India',
                    'Postal Address': data['Postal Address'],
                    'PinCode': data['Pin Code'],
                    'Phone1': data['Phone Office 1'],
                    'Phone2': data['Phone Office 2'],
                    'Phone3': data['Phone Residence 1'],
                    'Phone4': data['Phone Residence 2'],
                    'Phone5': '',
                    'Images URL': '',
                    'Working Hours': 'Monday - Friday: 10 AM - 5 PM, Saturday: 10 AM - 1 PM',
                    'Details': 'Contact us or use the live chat feature to get more details about our school.',
                    'Services Offered': '',
                    'FAX No': data['FAX No'],
                    'Mail': data['Email'],
                    'Website': data['Website'],
                    'Year of Foundation': data['Year of Foundation'],
                    'Date of First Openning of School': data['Date of First Openning of School'],
                    'Name of Principal/ Head of Institution': data['Name of Principal/ Head of Institution'],
                    'Sex': data['Sex'],
                    'Principal Education/Professional Qualifications': data['Principal Education/Professional Qualifications'],
                    'Number of Experience Years': data['Number of Experience Years'],
                    'Administrative': data['Administrative'],
                    'Teaching': data['Teaching'],
                    'Status of The School': data['Status of The School'],
                    'Type of affiliation': data['Type of affiliation'],
                    'Affiliation Period From': data['Affiliation Period From'],
                    'Affiliation Period To': data['Affiliation Period To'],
                    'Name of Trust/ Society/ Managing Committee': data['Name of Trust/ Society/ Managing Committee'],
                    'extra': data['extra']})

        except Exception as e:
            print "\n\n\n\n"
            print "Error: ", response
            print "Error exception: ", e
            with open("new_total_missed.csv","a") as total_failed:
                fieldnames = ['response','error message']
                writer = csv.DictWriter(total_failed,fieldnames=fieldnames)
                writer.writerow({'response' : response, 'error message':e});
            raise
            print "\n\n\n"
