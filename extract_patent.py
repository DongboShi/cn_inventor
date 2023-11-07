# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 23:04:45 2023

@author: Killlua
"""

import os
import json
from tqdm import tqdm
from lxml import etree
from urllib import parse
import argparse

parser = argparse.ArgumentParser(description='patents_analysis')
parser.add_argument('-input', '--arg1', type=str, help='input folder')
parser.add_argument('-output', '--arg2', type=str, help='output folder')

args = parser.parse_args()

print('arg1:', args.arg1)
print('arg2:', args.arg2)

def show_files(path, all_files):
    file_list = os.listdir(path)
    for file in file_list:
        cur_path = os.path.join(path, file)
        if os.path.isdir(cur_path):
            show_files(cur_path, all_files)
        else:
            all_files.append(file)
    return all_files

if __name__ == "__main__":
    # 提取文件夹内所有文件
    patents = show_files(args.arg1, [])
    desc = []
    for patent in tqdm(patents, desc='patents_analysis', total=len(patents)):
        h_index = f'{patent}'.find(".html")
        publn = f'{patent[:h_index]}'
        url = f"https://patents.google.com/patent/{publn}"
        with open(f'html/{patent}', mode='r', encoding='utf-8') as fp:
            html = fp.read()
        tree = etree.HTML(html)
        
        # 提取description（这里description的内容未作任何处理）
        description_lst = tree.xpath('//section[@itemprop="description"]//text()')
        description = "".join(description_lst)
        
        # 部分专利描述部分有图片
        patent_image_lst = tree.xpath('//div[@class="patent-image"]/a/@href')
    
        # 提取Patent Citations
        patent_citations = []
        pc_elements = tree.xpath('//tr[@itemprop="backwardReferences"]')
        if pc_elements:
            for pc in pc_elements:
                pc_row = dict()
                pc_html = etree.tostring(pc, pretty_print=True).decode('utf-8')
                pc_tree = etree.HTML(pc_html)
                href_raw = pc_tree.xpath('//a/@href')
                if href_raw:
                    href = parse.urljoin(url,href_raw[0])
                else:
                    href = ''
                pn = ''.join(pc_tree.xpath('//span[@itemprop="publicationNumber"]/text()')).strip()
                pl = ''.join(pc_tree.xpath('//span[@itemprop="primaryLanguage"]/text()')).strip()
                ec = ''.join(pc_tree.xpath('//span[@itemprop="examinerCited"]/text()')).strip()
                prd = ''.join(pc_tree.xpath('//td[@itemprop="priorityDate"]/text()')).strip()
                pud = ''.join(pc_tree.xpath('//td[@itemprop="publicationDate"]/text()')).strip()
                ae = ''.join(pc_tree.xpath('//span[@itemprop="assigneeOriginal"]/text()')).strip()
                tl = ''.join(pc_tree.xpath('//td[@itemprop="title"]/text()')).strip()
                
                pc_row['href'] = href
                pn_mix = f'{pn}({pl}){ec}'
                pc_row['Publication number'] = pn_mix
                pc_row['Priority date'] = prd
                pc_row['Publication date'] = pud
                pc_row['Assignee'] = ae
                pc_row['Title'] = tl
                patent_citations.append(pc_row)
                    
        # 提取Family Cites Families
        fam_cites_fam = []
        fc_elements = tree.xpath('//tr[@itemprop="backwardReferencesFamily"]')
        if fc_elements:
            for fc in fc_elements:
                fc_row = dict()
                fc_html = etree.tostring(fc, pretty_print=True).decode('utf-8')
                fc_tree = etree.HTML(fc_html)      
                href_raw = fc_tree.xpath('//a/@href')
                if href_raw:
                    href = parse.urljoin(url,href_raw[0])
                else:
                    href = ''
                pn = ''.join(fc_tree.xpath('//span[@itemprop="publicationNumber"]/text()')).strip()
                pl = ''.join(fc_tree.xpath('//span[@itemprop="primaryLanguage"]/text()')).strip()
                ec = ''.join(fc_tree.xpath('//span[@itemprop="examinerCited"]/text()')).strip()
                prd = ''.join(fc_tree.xpath('//td[@itemprop="priorityDate"]/text()')).strip()
                pud = ''.join(fc_tree.xpath('//td[@itemprop="publicationDate"]/text()')).strip()
                ae = ''.join(fc_tree.xpath('//span[@itemprop="assigneeOriginal"]/text()')).strip()
                tl = ''.join(fc_tree.xpath('//td[@itemprop="title"]/text()')).strip()
                
                fc_row['href'] = href
                pn_mix = f'{pn}({pl}){ec}'
                fc_row['Publication number'] = pn_mix
                fc_row['Priority date'] = prd
                fc_row['Publication date'] = pud
                fc_row['Assignee'] = ae
                fc_row['Title'] = tl
                fam_cites_fam.append(fc_row)
                    
        # 提取Legal Events
        legal_events = []
        legal_elements = tree.xpath('//tr[@itemprop="legalEvents"]')
        if legal_elements:
            for legal in legal_elements:
                legal_row = dict()
                legal_html = etree.tostring(legal, pretty_print=True).decode('utf-8')
                legal_tree = etree.HTML(legal_html)
                date = ''.join(legal_tree.xpath('//time[@itemprop="date"]/text()')).strip()
                code = ''.join(legal_tree.xpath('//td[@itemprop="code"]/text()')).strip()
                title = ''.join(legal_tree.xpath('//td[@itemprop="title"]/text()')).strip()
                legal_desc_lst = legal_tree.xpath('//td//p[@itemprop="attributes"]//text()')
                if legal_desc_lst:
                    legal_description = ''.join([x.strip() for x in legal_desc_lst]).strip()
                else:
                    legal_description = ''
                legal_row['Date'] = date
                legal_row['Code'] = code
                legal_row['Title'] = title
                legal_row['Description'] = legal_description
                legal_events.append(legal_row)
                
        desc.append({'publn' : publn,
                     'description' : description,
                     'patent_image' : patent_image_lst,
                     'patent_citations' : patent_citations,
                     'family_cites_families' : fam_cites_fam,
                     'legal_events' : legal_events}
                    )
    with open(f'{args.arg2}/patent_content.json', mode='w', encoding='utf-8') as fj:
        json.dump(desc, fp = fj, ensure_ascii = False, indent = 4, sort_keys = False)