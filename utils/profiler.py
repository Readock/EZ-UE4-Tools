import cProfile

# # example usage:
# with Profiler():
#   method_to_profile()

class Profiler():
    ''' Utility class to profile '''
    pr = None

    def __enter__(self):
        ''' Starts profiling '''
        self.pr = cProfile.Profile()
        self.pr.enable()
        return self

    def __exit__(self, type, value, traceback):
        ''' End profiling and print status '''
        self.pr.disable()
        self.pr.print_stats()