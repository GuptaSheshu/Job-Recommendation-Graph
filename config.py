import json
class JobPosting():
    """Class to warp all the information in the Job posting.
    """
    def __init__(self, job_title, company_name, location, job_url, job_description=None,
                 basic_qualificaiton = None,
                 preferred_qualification = None):
        self.job_title = job_title
        self.company_name = company_name
        self.location = location
        self.job_url = job_url
        self.job_desc = job_description
        self.base_qual = basic_qualificaiton
        self.pref_qual = preferred_qualification
    
    def print_info(self):
        print("Job title :-", self.job_title)
        print("Company Name :-", self.company_name)
        print("Location :-", self.location)

def get_cache(CACHE_FILENAME):
    """Read CACHE file if available.

    Args:
        CACHE_FILENAME (str): JSON cache file name

    Returns:
        dict: a dictionary describing the content in the cache file
    """
    try:
        with open(CACHE_FILENAME, 'r') as fw:
            data = json.load(fw)
    except:
        data = {}
    return data

def save_cache(CACHE_FILENAME, job_info_list, typ):
    """Save Cache file to local system.

    Args:
        CACHE_FILENAME (str): JSON cache file name
        job_info_list (List): A list of dictionary describing the job
        typ (str): a unique identifier for cache to recognize the job source. 
    """
    try:
        with open(CACHE_FILENAME, 'r') as fw:
            data = json.load(fw)
    except:
        data = {}
    
    data['Job_info_list_'+str(typ)] = job_info_list
    with open(CACHE_FILENAME, 'w') as fw:
        json.dump(data, fw)

def load_cache(data):
    """Loading the cache data

    Args:
        data (dict): a dictionary loaded from cache JSON file.

    Returns:
        List: a list of job information taken from cache and wrap it in
        'JobPosting' class.
    """
    PostList = []
    for key, val_list in data.items():
        PostList += wrap_class(val_list)
    return PostList

def wrap_class(job_info_list):
    """Wrapping the job information to JobPosting class.

    Args:
        job_info_list (dict): a dictionary containing job information.

    Returns:
        List: a list of job information taken from cache and wrap it in
        'JobPosting' class.
    """
    PostList = []
    for idx, job in enumerate(job_info_list):
        temp = JobPosting(job_title=job['job_title'], company_name = job['company_name'], location=job['location'],
                                job_url=job['job_url'], job_description=job['desc'],
                                basic_qualificaiton=job['basic_qual'], preferred_qualification=job['pref_qual'])
        PostList.append(temp)
    return PostList

def get_unique_loc(PostList):
    """Get unique location from the job database

    Args:
        PostList (List): a list of job information wrapped in 'JobPosting'
        class

    Returns:
        tuple: a tuple of dictionary containing unique location outside and
        inside US.
    """
    loc = []
    for idx, val in enumerate(PostList):
        if(idx>=40):
            if(val.location is not None):
                PostList[idx].location = 'usa, '+ PostList[idx].location
            else:
                PostList[idx].location = 'usa'
        try:
            temp = val.location.strip().lower()
        except:
            temp = ''
        loc.append(temp)
    
    loc_dict_outside = {}
    loc_dict_us = {}
    tp = {'arlington':'tx','seattle':'wa','san francisco':'ca', 'north carolina':'nc', 'arizona':'az'}
    for id, loc_val in enumerate(loc):
        try:
            if(loc_val[:3]=='usa'):
                tt = loc_val.split(',')[-1].strip()
                if(tt in list(tp.keys())):
                    tt = tp[tt]
                loc_dict_us[tt] += 1
            else:
                tt = loc_val.split(',')[-1].strip()
                loc_dict_outside[tt] += 1
        except:
            if(loc_val[:3]=='usa'):
                tt = loc_val.split(',')[-1].strip()
                if(tt in list(tp.keys())):
                    tt = tp[tt]
                loc_dict_us[tt] = 1
            else:
                tt = loc_val.split(',')[-1].strip()
                loc_dict_outside[tt] = 1
    return loc_dict_us, loc_dict_outside

def get_unique_company(PostList):
    """Get unique company list from the job database.

    Args:
        PostList (List): a list of job information wrapped in 'JobPosting'
        class

    Returns:
        dict : a dictionary whose keys are company and value is the occurence
        of the company.
    """
    cmp = []
    for idx, val in enumerate(PostList):
        try:
            temp = val.company_name.strip().lower()
        except:
            temp = ''
        cmp.append(temp)
    
    cmp_dict = {}
    for id, cmp_val in enumerate(cmp):
        try:
            cmp_dict[cmp_val] += 1
        except:
            cmp_dict[cmp_val] = 1
    return cmp_dict


def get_url_glassdoor():
    """URL for glassdoor

    Returns:
        dict: a dictionary who keys describing the query and value describing URL.
    """
    query_dict = {
        'software-engineer':'https://www.glassdoor.com/Job/united-states-software-engineer-jobs-SRCH_IL.0,13_IN1_KO14,31.htm?minRating=4.00&employerSizes=5',
        'machine-learning':'https://www.glassdoor.com/Job/us-machine-learning-jobs-SRCH_IL.0,2_IN1_KO3,19.htm?minRating=4.00&employerSizes=5',
        'mechanical-engineer':'https://www.glassdoor.com/Job/mechanical-engineer-jobs-SRCH_KO0,19.htm?minRating=4.00&employerSizes=5',
        'electrical-engineer':'https://www.glassdoor.com/Job/electrical-engineer-jobs-SRCH_KO0,19.htm?minRating=4.00&employerSizes=5',
        'data-engineer':'https://www.glassdoor.com/Job/data-engineer-jobs-SRCH_KO0,13.htm?minRating=4.0&employerSizes=5'
    }
    company_dict = {
        'apple':'https://www.glassdoor.com/Jobs/Apple-Jobs-E1138.htm?filter.countryId=1',
        'Microsoft':'https://www.glassdoor.com/Jobs/Microsoft-Jobs-E1651.htm?filter.countryId=1',
        'Meta':'https://www.glassdoor.com/Jobs/Meta-Jobs-E40772.htm?filter.countryId=1',
        'Google':'https://www.glassdoor.com/Jobs/Google-Jobs-E9079.htm?filter.countryId=1',
        'Nvidia':'https://www.glassdoor.com/Jobs/NVIDIA-Jobs-E7633.htm?filter.countryId=1',
        'Intel':'https://www.glassdoor.com/Jobs/Intel-Corporation-Jobs-E1519.htm?filter.countryId=1'
    }
    return query_dict, company_dict