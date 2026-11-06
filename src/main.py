from core.runner import Runner
from core.logger import configure_logging
from testers import (
    AlgorithmTester,
)
from testers.historical_test import TestHistorico
from testers.historical_comparison import FreezingCoefTester
from testers.test_stop_criteria import FreezingTempTester
from testers.max_temp_tester import MaxTempTester

if __name__ == '__main__':
    configure_logging("INFO")

    runner = Runner()    
    runner.add_tester(AlgorithmTester(num_runs=30))
    # runner.add_tester(TestHistorico())
    # runner.add_tester(FreezingCoefTester())
    # runner.add_tester(FreezingTempTester())
    # runner.add_tester(MaxTempTester())
    
    runner.run()
