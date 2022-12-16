from config import *
from amazon_data_scrapping import *
from glassdoor_data_scrapping import *
from graph import *
import flask
from flask import Flask, render_template, request


CACHE_FILENAME = 'data.json'


def make_request_with_cache():
    cache_dict = get_cache(CACHE_FILENAME)
    if(cache_dict):
        print("Cache hit!")
        print("Loading data from cache ... ")
        PostList = load_cache(cache_dict)
    else:
        print("No Cache Found!")
        print("Loading the data from APIs .... ")
        job_info_list = []
        job_info = amazon_main()
        job_info_list += job_info
        save_cache(CACHE_FILENAME, job_info, 'Amazon')
        print('------ Saving Cache for Amazon openings ---------')
        print('\nStarting Glassdoor APIs call, Please wait..... ')
        job_info = glassdoor_main()
        job_info_list += job_info
        save_cache(CACHE_FILENAME, job_info, 'Glassdoor')
        print('------ Saving Cache for Glassdoor openings ---------')
        PostList = wrap_class(job_info_list)
    
    return PostList
    
PostList = make_request_with_cache()

job_graph = Graph()

# Parent Node --> Location, Full/Intern, Company Name, Keyword
Nparent = 4
parent_node = ['Location', 'Full/Intern', 'Company Name', 'Keyword']

# Add all the node in job_graph
for idx, val in enumerate(PostList):
    job_graph.add_node(idx, val)

loc_dict_us, loc_dict_outside = get_unique_loc(PostList)
cmp_dict = get_unique_company(PostList)

# Add Parent Node with special keys to recognize it later.
for idx, (key, val) in enumerate(cmp_dict.items()):
    job_graph.add_node('c/'+str(key), key)

for idx, (key, val) in enumerate(loc_dict_us.items()):
    job_graph.add_node('lu/'+str(key), key)

job_graph.add_node('lu/outside_usa', 'outside_usa')

job_graph.add_node('FI/full', 'full')
job_graph.add_node('FI/intern', 'intern')

# Connect all the edges based on location
for idx1, (key1, val1) in enumerate(job_graph.node_info.items()):
    if(isinstance(key1, int)):
        continue    
    parent = key1.split('/')[0]
    for idx2, (key2, val2) in enumerate(job_graph.node_info.items()):
        if(parent in ['c'] and isinstance(key2, int)):
            if(val1.lower() == val2.company_name.lower()):
                job_graph.add_edge(key1, key2)
                job_graph.add_edge(key2, key1)
        
        if(isinstance(key2, int)):
            if(parent in ['lu', 'lo']):
                if(val2.location.lower()[:3]=='usa'):
                    if(val1.lower() == val2.location.lower().split(',')[-1].strip()):
                        job_graph.add_edge(key1, key2)
                        job_graph.add_edge(key2, key1)
                elif (len(val1)>=4) and (val1 not in ['virtual','remote']):
                    job_graph.add_edge('lu/outside_usa', key2)
                    job_graph.add_edge(key2, 'lu/outside_usa')    
        
        if(isinstance(key2, int)):
            if(parent in ['FI']):
                ispresent = (val1=='intern') and (val1 in val2.job_title.lower())
                if(ispresent):
                    job_graph.add_edge('FI/intern', key2)
                    job_graph.add_edge(key2, 'FI/intern')
                elif(val1=='full' and ('intern' not in val2.job_title.lower())):
                    job_graph.add_edge('FI/full', key2)
                    job_graph.add_edge(key2, 'FI/full')



# loc = input("Location (States) or Outside USA or USA or ALL or remote:- ")
df_abr = pd.read_csv('data_abrev.csv')
df_abr_dict = {}
for i in range(len(df_abr)):
    df_abr_dict[df_abr.state[i]]=df_abr.code[i]

df_abr_dict['USA'] = 'USA'
df_abr_dict['ALL'] = 'ALL'
# df_abr_dict['outside_usa'] = 'outside_usa'

# Flask 
app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html", state_list=list(df_abr['state'].to_list())+['ALL', 'Outside USA', 'USA'], fi_list=["Full", "Intern"], cmp_list=[k.capitalize() for k in cmp_dict.keys()]+['ALL'],
                           result_list=None)

@app.route("/display_posts", methods=["POST"])
def display_posts():
    loc = request.form.get('loc')
    fi = request.form.get('position_type')
    cmp = request.form.get('company_name')
    keyword = request.form.get('fname')
    # loc = request.form.get('loc')
    
    print(loc,fi,cmp, keyword)
    result = main(loc, fi, cmp, keyword)
    print(result)
    return render_template("index.html", state_list=list(df_abr['state'].to_list())+['ALL', 'Outside USA', 'USA'], fi_list=["Full", "Intern"], cmp_list=[k.capitalize() for k in cmp_dict.keys()]+['ALL'],
                           result_list=result)
    

def main(loc, fi, cmp, keyword):
    df_abr_dict['outside_usa'] = 'outside_usa'
    usr_loc = df_abr_dict[loc.strip()].lower()
    
    # fi = input("Full or intern ? ")
    usr_fi = fi.strip().lower()
    
    # cmp = input("Company Name or ALL :- ")
    usr_cmp = cmp.strip().lower()
    
    key_act_loc, key_act_cmp, key_act_fi = [],[],[]
    if(usr_loc=='usa'):
        temp_li = ['lu/' + ss for ss in list(loc_dict_us.keys())]
        key_act_loc += temp_li
    elif(usr_loc=='all'):
        temp_li = ['lu/' + ss for ss in list(loc_dict_us.keys())]
        key_act_loc += temp_li
        key_act_loc += ['lu/outside_usa']
    else:
        key_act_loc.append('lu/'+usr_loc)
    
    if(usr_cmp == 'all'):
        temp_li = ['c/' + ss for ss in list(cmp_dict.keys())]
        key_act_cmp += temp_li
    else:
        key_act_cmp.append('c/'+usr_cmp)
    key_act_fi.append('FI/'+usr_fi)

    results_loc, results_cmp, results_fi = [],[],[]

    for idx, (key, val) in enumerate(job_graph.adj_list.items()):
        if(isinstance(key, str)):
            continue

        for key_ac in key_act_loc:
            if(key_ac in val):
                results_loc.append(key)

        for key_ac in key_act_cmp:
            if(key_ac in val):
                results_cmp.append(key)

        for key_ac in key_act_fi:
            if(key_ac in val):
                results_fi.append(key)
    
    final_results = list(set(results_loc) & set(results_cmp) & set(results_fi))
    final_results_obj = [job_graph.node_info[x] for x in final_results]
    for i in range(len(final_results)):
        temptt = job_graph.node_info[final_results[i]]
        print("{}th Job".format(i+1))
        print(temptt.print_info())
        # print("Job title :-", temptt.job_title)
        # print("Company Name :-", temptt.company_name)
        # print("Location :-", temptt.location)
        print('-----------------')
    
    keyword_final = []
    keyword_list = keyword.split()
    for i, vm in enumerate(final_results_obj):
        for kk in keyword_list:
            if(kk in vm.job_title) or (kk in vm.job_desc) or (kk in vm.base_qual) or (kk in vm.pref_qual):
                keyword_final.append(vm)
    if(keyword):
        return keyword_final
    return final_results_obj
           
    
if __name__== '__main__':
    app.run()