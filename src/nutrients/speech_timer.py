import pyttsx3
import numpy as np
import time
from datetime import timedelta
import math
from beepy import beep

class Timer:
    """
    small timer. Watch out! The program can't deal with very small time differences
    because then the speech function is too slow.

    sms:    samples per sequence
    """
    def __init__(self, cycles = np.inf, timings = {}, prep_time = 10, sps = 1):
        self.cycles = cycles
        self.steps_cycle = len(timings)
        self.sps = sps
        
        self.ask_for_input()
        self.timings = self.prepare_timings(timings) # should be in seconds
        
        self.run(prep_time)

    def ask_for_input(self):
        pass
        # if self.timings == {}:
        #     input("specify timing cylce in seconds")

    def prepare_timings(self, timings):
        max_key = max(list(timings.keys()))

        for c in range(self.cycles):
            timings.update( {key+max_key:value for (key,value) in timings.items()} )
        
        return timings

    def run(self, prep_time):
        timings = self.timings.copy()
        print("\nprogram starting. Prepare!")

        time.sleep(prep_time)
        beep(sound=1)
        time.sleep(.4)
        beep(sound=1)
        time.sleep(.4)
        beep(sound=1)

        self.engine = pyttsx3.init()
        start = math.floor(time.time())
        step = self.steps_cycle-1
        sample = self.sps
        while timings != {}:
            elapsed = math.floor(time.time()-start)
            
            if elapsed in timings.keys():
                step += 1
                if step == self.steps_cycle:
                    print("\n-----------------------------------------------------")
                    print("working on samples {}. Time elapsed {}\n".format(sample, timedelta(seconds=elapsed)))
                    step = 1
                    sample += self.sps
                
                event = timings.pop(elapsed)
                print("step {}: {}".format(step, event))
                self.engine.say(event)
                self.engine.runAndWait()

            

            

            


