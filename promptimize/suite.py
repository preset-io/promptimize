class Suite:
    """a collection of use cases to be tested"""

    def __init__(self, use_cases):
        self.use_cases = use_cases

    def execute(self, verbose):
        for use_case in self.use_cases:
            use_case.run()
            use_case.test()
            use_case.print(verbose=verbose)
