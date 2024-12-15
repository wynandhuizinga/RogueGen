import time


class Logger():

    def __init__(self, filepath, logfilename, perfname):
        self.filepath = filepath
        self.logfilename = self.filepath+logfilename
        self.perfname = self.filepath+perfname
        self.time_since_last_call = time.time()
        self.timing_data = {}
        self.averages = {}

    def logGeneration(self,string):
        self.store(string)
        
    def logTime(self,step):
        timing = time.time()-self.time_since_last_call
        message = step+" took (seconds) \t"+str("{:.2f}".format(timing))
        print(message)
        self.record_step(step,timing)
        self.time_since_last_call = time.time()
        with open(self.perfname, 'a', encoding='utf-8') as file:
            file.write('\n'+message)
    
    def store(self,string):
        with open(self.logfilename, 'a', encoding='utf-8') as file:
            file.write('\n======================\n'+string)
            
    def record_step(self, step_name, timing):
        if step_name in self.timing_data:
            self.timing_data[step_name]['total_time'] += timing
            self.timing_data[step_name]['count'] += 1
        else:
            self.timing_data[step_name] = {'total_time': timing, 'count': 1}
        self.averages = {step: data['total_time'] / data['count'] for step, data in self.timing_data.items()}
        #print(self.averages)
        
    def record_averages(self):
        with open(self.perfname, 'a', encoding='utf-8') as file:
            file.write("\n============================\nAverage step performance data:\n============================\n")
            for step, data in self.averages.items():
                file.write(f"{step}: {data}\n")
            file.write("\n============================\n============================\n")
