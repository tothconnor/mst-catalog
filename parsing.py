#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
from bs4 import BeautifulSoup
import time
import json

# url of the page that has the menu on it
ROOT_ADDR = 'http://catalog.mst.edu';
MENU_ADDR = 'http://catalog.mst.edu/undergraduate/degreeprogramsandcourses/#text';


def get_html_from_url ( url ):

  # open a connection to the url                              
  socket = urllib2.urlopen( url );

  # get the source code of the web-page
  html_data = socket.read();

  # close the connection to the url
  socket.close();

  # return the HTML source code
  return html_data;


def get_urls ( ):
  
  # get the html from the menu page
  pagedata = get_html_from_url(MENU_ADDR);

  # set up the parser so we can get info
  soup = BeautifulSoup(pagedata, 'html.parser');

  # set up an aggregator to store the urls
  urls = [];

  # get the list of department program links
  menu_list = soup.find('ul', id='/undergraduate/degreeprogramsandcourses/');

  # get each element of that list
  menu_list = menu_list.find_all('li');

  # for each element of that list
  for item in menu_list:

    # the relative URL is the anchor element's href property
    url = item.find('a')['href'];

    # on the offchance that there may be some non-relative
    # only if the URL starts with a '/' is prepended with the
    # root URL
    if url[0] == '/':
      url = ROOT_ADDR + url;

    # push the new URL to the aggregation of urls
    urls += [url];

  # return all URLs
  return urls;


def get_class_tuples_from_html ( html ):
  
  # set up the parser so we can get info
  soup = BeautifulSoup(html, 'html.parser');

  # find all courseblocks in which each course is described
  blocks = soup.find_all('div', class_='courseblock');

  # set up an aggregator of course tuples
  tuples = [];

  # for each of these split into component parts
  for block in blocks:

    # differentiate the two main elements of the block
    titleblock = block.find(class_='courseblocktitle');
    descblock = block.find(class_='courseblockdesc');

    # obtain the dept and course number
    dept_plus_num = urllib2.unquote(titleblock['id']);
    
    # obtain the course name
    course_name = '';
    for string in titleblock.strings:
      course_name += string;
    
    # obtain the description
    description = '';
    for string in descblock.strings:
      description += string;

    # push the new tuple to the aggregation
    tuples += [( dept_plus_num, course_name, description )];

  # return all tuples
  return tuples;


def main ( ):
  # get the urls we need to visit to get class information
  urls = get_urls();

  # master object
  master = {'courses':{}, 'departments':[]};

  # file to store all the tuples in
  file = open('courses.json', 'w');

  # for each url we visit
  for url in urls:

    # get the HTML source code from that URL
    html = get_html_from_url(url);

    # create the course tuples from those pages
    tuples = get_class_tuples_from_html(html);


    # the dept name changes every url, so any tuple
    # will work
    if len(tuples) > 0:
      # dept name
      dept_name = '';
      first_flag = True;
      
      for word in tuples[0][0].split(' '):

        # if the word is a number, we are done
        # and need not continue
        if (word.isdigit()):
          break;

        # do not add a space before the word
        # if it is the first word being added
        if first_flag:
          first_flag = False;
          dept_name += word;

        # otherwise add a space before the word
        else:
          dept_name += ' ' + word;

      master['departments'] += [dept_name];

    # add the data into the JSON object
    for tup in tuples:

      tup_obj = {
        'course_name': tup[1],
        'description': tup[2],
        'address'    : url
      };

      # push the tuple to the master with a key value
      # of the course dept + number
      master['courses'][tup[0]] = tup_obj;

  # write the file JSON equivalent (pretty too!)
  file.write( json.dumps(master, indent = 2, sort_keys=True, separators=(',', ': ')) );

  # close the file
  file.close( );


main ( );