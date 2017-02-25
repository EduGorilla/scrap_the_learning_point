import csv
import scrapy
from bs4 import BeautifulSoup
from pathlib import Path
import logging


class QuotesSpider(scrapy.Spider):
    name = "dynamicscrapper"

    #  start_urls=['http://www.thelearningpoint.net/home/school-listings/cbse-13/Bayonet-School-Bayonet-School-C-O-Infantry-School--Mhow-1030454']

    def start_requests(self):
        base_url = 'http://www.thelearningpoint.net/system/app/pages/search?scope=search-site&q=school&offset='

        print "Scraping Started for "+base_url+". Please wait..."

        for counter in xrange(0, 57174, 10):
            url = base_url + str(counter)
            #print "Url to be scrapped : "+url
            yield scrapy.Request(url=url, callback=self.parse_page)

    def parse_page(self, response):
        page = response.xpath('//td[@id="col0"]').css('div.sites-search-result h3 a::attr(href)').extract()
        for i in page:
            link = response.urljoin(i)
            #print "next page", link
            # inp = input()
            try:
                yield scrapy.Request(url=link, callback=self.parse_school)
            except:
                print "could not go to indivitual school"
                #inp = input();

    def parse_school(self, response):
        #print "Scrapping school data: ", response;
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
            for fieldValue in dataToScrap:
                data[fieldValue] = unicode('');

            point = 0
            page = BeautifulSoup(response.css('body').extract()[0], 'html.parser').find_all('td')

            for fieldValue in dataToScrap:
                try:
                    for val, i in enumerate(page):
                        if i.b is not None and i.b.string is not None and i.b.string.strip().find(fieldValue) is not -1:
                            data[fieldValue] = page[val + 1].string.strip();
                except Exception as e:
                    print fieldValue + " not found : " + str(e);
                    data[fieldValue] = unicode('N/A');

            try:
                for val, i in enumerate(page):
                    if i.b is not None and i.b.string is not None and i.b.string.strip().lower().find('pin') is not -1:
                        data['Pin Code'] = page[val + 1].string.strip();
            except Exception as e:
                print "Pin Code not found : "+str(e);

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

            #print "Showing data: ", data

            hasData = False;

            for fieldValue in dataToScrap:
                if(data[fieldValue]!=unicode('')):
                    hasData = True;

            if(hasData==False):
                with open("partial_missed.csv","a") as total_failed:
                    fieldnames = ['links']
                    writer = csv.DictWriter(total_failed,fieldnames=fieldnames)
                    writer.writerow({'links' : response});
                    return;
            

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
                with open("output/" + data['State'].lower() + ".csv", "wb") as myFile:
                    writer = csv.DictWriter(myFile, fieldnames=fieldnames)
                    writer.writeheader()

            with open("output/" + data['State'].lower() + ".csv", "a") as myFile:
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
                    'Principal Education/Professional Qualifications': data[
                        'Principal Education/Professional Qualifications'],
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
            with open("total_missed.csv","a") as total_failed:
                fieldnames = ['response','error message']
                writer = csv.DictWriter(total_failed,fieldnames=fieldnames)
                writer.writerow({'response' : response, 'error message':e});
            raise
            print "\n\n\n"
