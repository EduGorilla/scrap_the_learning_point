import csv
import scrapy
from bs4 import BeautifulSoup
from pathlib import Path
import logging
import os
import traceback


def make_sure_path_exists(directoryName):
    try:
        if not os.path.exists(directoryName):
            os.makedirs(directoryName);
    except OSError as exception:
        print "Unable to create directory" + directoryName;

class DynamicSpider(scrapy.Spider):
    name = "dynamicscrapper"

    count_total_scrapped = 0;
    count_no_data = 0;
    count_missed_totally = 0;

    #  start_urls=['http://www.thelearningpoint.net/home/school-listings/cbse-13/Bayonet-School-Bayonet-School-C-O-Infantry-School--Mhow-1030454']

    def start_requests(self):
        base_url = 'http://www.thelearningpoint.net/system/app/pages/search?scope=search-site&q=school&offset='

        print "Scraping Started for "+base_url+". Please wait..."
        make_sure_path_exists('output');
        make_sure_path_exists('status');
        for counter in xrange(0, 57174, 10):
            url = base_url + str(counter)
            #print "Url to be scrapped : "+url
            yield scrapy.Request(url=url, callback=self.parse_page)

    def parse_page(self, response):
        schoolLinks = response.xpath('//td[@id="col0"]').css('div.sites-search-result h3 a::attr(href)').extract()
        for schoolLink in schoolLinks:
            link = response.urljoin(schoolLink);
            #link = "http://www.thelearningpoint.net/home/school-listings/maharashtra-ssc-39/2306034-TOP-HIGH-SCHOOL--TOP";
            #print "next schoolLinks", link
            # inp = input()
            try:
                yield scrapy.Request(url=link, callback=self.parse_school)
            except:
                print "could not go to indivitual school"
                #inp = input();

    def parse_school(self, response):
        current_url = response.request.url;
        #print "Scrapping school data: ", current_url;
        self.count_total_scrapped = self.count_total_scrapped+1;
        if(self.count_total_scrapped%10==0):
            print "Scrapped count_total_scrapped : "+str(self.count_total_scrapped)+" Count_no_data : "+str(self.count_no_data)+" Count_missed_totally : "+str(self.count_missed_totally);
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
            bodyNode = BeautifulSoup(response.css('body').extract()[0], 'html.parser');
            tdNodes = bodyNode.find_all('td');
            divNodes = bodyNode.find_all('div');

            for fieldValue in dataToScrap:
                try:
                    for tdCount, tdValue in enumerate(tdNodes):
                        if tdValue.b is not None and tdValue.b.string is not None and tdValue.b.string.strip().find(fieldValue) is not -1:
                            data[fieldValue] = tdNodes[tdCount + 1].string.strip();
                except Exception as e:
                    print fieldValue + " not found : " + str(e);
                    data[fieldValue] = unicode('N/A');

            try:
                for tdCount, tdValue in enumerate(tdNodes):
                    if tdValue.b is not None and tdValue.b.string is not None and tdValue.b.string.strip().lower().find('pin') is not -1:
                        data['Pin Code'] = tdNodes[tdCount + 1].string.strip();
            except Exception as e:
                print "Pin Code not found : "+str(e);

            try:
                phoneNumber1 = data['STD'] + tdNodes[point + 1].string.strip();
                data['Phone Office 1'] = ''.join(filter(str.isdigit, phoneNumber1));
            except:
                #print "Phone Office 1 not found"
                data['Phone Office 1'] = unicode('')
            try:
                data['Phone Office 2'] = data['STD'] + tdNodes[point + 2].string.strip();
            except:
                #print "Phone Office 2 not found"
                data['Phone Office 2'] = unicode('')
            try:
                data['Phone Residence 1'] = data['STD'] + tdNodes[point + 4].string.strip();
            except:
                #print "Phone Residence 1 not found"
                data['Phone Residence 1'] = unicode('')
            try:
                data['Phone Residence 2'] = data['STD'] + tdNodes[point + 5].string.strip();
            except:
                #print "Phone Residence 2 not found"
                data['Phone Residence 2'] = unicode('')

            #print "Showing data: ", data

            hasData = False;

            #Check if we have parsed at least some data points
            for fieldValue in dataToScrap:
                if(data[fieldValue]!=unicode('')):
                    hasData = True;
            if(data['Name of Institution']==unicode('')):
                hasData = False;

            if (hasData == False):
                # Trying to fetch Non-Table data:
                try:
                    for divCount, divValue in enumerate(divNodes):
                        boldNodes = divValue.find_all('b');
                        for boldCount, boldValue in enumerate(boldNodes):
                            headingNode = boldValue.find('font', {'color': '#cc0000'});
                            if (headingNode is not None and headingNode.text is not None):
                                boldHeading = headingNode.text;
                                boldContent = boldValue.find(text=True, recursive=False);
                                if (boldHeading.strip().lower().find('name')) is not -1:
                                    data['Name of Institution'] = boldContent;
                                elif (boldHeading.strip().lower().find('address')) is not -1:
                                    data['Postal Address'] = boldContent;
                                elif (boldHeading.strip().lower().find('district')) is not -1:
                                    data['District'] = boldContent;
                                elif (boldHeading.strip().lower().find('pin')) is not -1:
                                    data['Pin Code'] = boldContent;
                        fontNode = divValue.find('font', {'face': 'times new roman, serif'});
                        if fontNode is not None and fontNode.text is not None and fontNode.text.strip().find('Contact Details (Mobile Number/Email):') is not -1:
                            contactDetailDiv = divValue.find_next_sibling("div");
                            #print "divValue : " + str(divValue);
                            #print "fontValue : " + str(fontNode.string);
                            #print "ContactDetailDiv : "+str(contactDetailDiv.string);
                            contactDetails = contactDetailDiv.string.strip();
                            contactDetailArray = contactDetails.split('/');
                            if len(contactDetailArray) == 2:
                                contactPhoneNumber = contactDetailArray[0];
                                contactEmailId = contactDetailArray[1];
                                if contactPhoneNumber and not contactPhoneNumber.isspace():
                                    data['Phone Office 1'] = contactPhoneNumber;
                                if contactEmailId and not contactEmailId.isspace():
                                    data['Email'] = contactEmailId;
                    # Check if we have parsed at least some data points
                    for fieldValue in dataToScrap:
                        if (data[fieldValue] != unicode('')):
                            hasData = True;
                    if data['Name of Institution'] == unicode(''):
                        hasData = False;
                except Exception as e:
                    just_exception_string = traceback.format_exc();
                    print "Non Table data not found : " + str(just_exception_string);


            if(hasData==False):
                fieldnames = ['Partial Count','Failed Link'];
                checkFilePath = Path("status/" + "partial_missed.csv");
                if not checkFilePath.is_file():
                    with open("status/" + "partial_missed.csv", "wb") as myFile:
                        writer = csv.DictWriter(myFile, fieldnames=fieldnames)
                        writer.writeheader();
                with open("status/" + "partial_missed.csv","a") as total_failed:
                    writer = csv.DictWriter(total_failed,fieldnames=fieldnames);
                    self.count_no_data = self.count_no_data + 1;
                    writer.writerow({'Partial Count' : self.count_no_data, 'Failed Link':response});
                    return;
            

            fieldnames = ['Name', 'Affiliation Number', 'State', 'City', 'Locality', 'Country',
                          'Postal Address', 'PinCode', 'Phone1', 'Phone2', 'Phone3', 'Phone4', 'Phone5',
                          'Images URL', 'Working Hours', 'Details', 'Services Offered',
                          'FAX No', 'Mail', 'Website', 'Year of Foundation',
                          'Date of First Openning of School', 'Name of Principal/ Head of Institution', 'Sex',
                          'Principal Education/Professional Qualifications', 'Number of Experience Years',
                          'Administrative', 'Teaching', 'Status of The School', 'Type of affiliation',
                          'Affiliation Period From', 'Affiliation Period To',
                          'Name of Trust/ Society/ Managing Committee', 'extra', 'Source URL'];
            checkFilePath = Path("output/" + data['State'].lower() + ".csv");
            if not checkFilePath.is_file():
                with open("output/" + data['State'].lower() + ".csv", "wb") as myFile:
                    writer = csv.DictWriter(myFile, fieldnames=fieldnames)
                    writer.writeheader();

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
                    'extra': data['extra'],
                    'Source URL': current_url
                })

        except Exception as e:
            print "\n\n\n\n"
            print "Error: ", response
            self.count_missed_totally = self.count_missed_totally + 1;
            print "Error exception: ", e;
            fieldnames = ['response', 'error message'];
            checkFilePath = Path("status/" + "total_missed.csv");
            if not checkFilePath.is_file():
                with open("output/" + "total_missed.csv", "wb") as myFile:
                    writer = csv.DictWriter(myFile, fieldnames=fieldnames)
                    writer.writeheader();
            with open("status/" + "total_missed.csv","a") as total_failed:
                writer = csv.DictWriter(total_failed,fieldnames=fieldnames)
                writer.writerow({'response' : response, 'error message':e});
            print "\n\n\n";