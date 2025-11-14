
import unittest
from etl.procurement.risk_calculator import RiskCalculator

class TestRiskCalculator(unittest.TestCase):

    def setUp(self):
        """Set up a RiskCalculator instance for testing."""
        country_risk_map = {
            'HighRiskCountry': 'High Risk',
            'MediumRiskCountry': 'Medium Risk',
            'LowRiskCountry': 'Low Risk'
        }
        company_total_spend = 1000000
        self.risk_calculator = RiskCalculator(country_risk_map, company_total_spend)

    def test_calculate_country_risk(self):
        """Test the calculate_country_risk method."""
        self.assertEqual(self.risk_calculator.calculate_country_risk('HighRiskCountry'), 30)
        self.assertEqual(self.risk_calculator.calculate_country_risk('MediumRiskCountry'), 15)
        self.assertEqual(self.risk_calculator.calculate_country_risk('LowRiskCountry'), 0)
        self.assertEqual(self.risk_calculator.calculate_country_risk('UnknownCountry'), 0) # Defaults to Low Risk

    def test_calculate_single_sourcing_risk(self):
        """Test the calculate_single_sourcing_risk method."""
        # No critical items
        self.assertEqual(self.risk_calculator.calculate_single_sourcing_risk([]), 0)

        # One single-sourced item
        critical_items_1 = [{'supplier_spend': 95, 'total_item_spend': 100}]
        self.assertEqual(self.risk_calculator.calculate_single_sourcing_risk(critical_items_1), 25)

        # Two single-sourced items
        critical_items_2 = [
            {'supplier_spend': 95, 'total_item_spend': 100},
            {'supplier_spend': 100, 'total_item_spend': 100}
        ]
        self.assertEqual(self.risk_calculator.calculate_single_sourcing_risk(critical_items_2), 40) # 25 + 15

        # One partially-sourced item
        critical_items_3 = [{'supplier_spend': 60, 'total_item_spend': 100}]
        self.assertEqual(self.risk_calculator.calculate_single_sourcing_risk(critical_items_3), 10)

        # Two partially-sourced items
        critical_items_4 = [
            {'supplier_spend': 60, 'total_item_spend': 100},
            {'supplier_spend': 70, 'total_item_spend': 100}
        ]
        self.assertEqual(self.risk_calculator.calculate_single_sourcing_risk(critical_items_4), 17.5) # 10 + 7.5

        # Mix of single and partially sourced
        critical_items_5 = [
            {'supplier_spend': 95, 'total_item_spend': 100},
            {'supplier_spend': 60, 'total_item_spend': 100}
        ]
        self.assertEqual(self.risk_calculator.calculate_single_sourcing_risk(critical_items_5), 32.5) # 25 + 7.5
        
        # Item with spend percentage < 50%
        critical_items_6 = [{'supplier_spend': 40, 'total_item_spend': 100}]
        self.assertEqual(self.risk_calculator.calculate_single_sourcing_risk(critical_items_6), 0)
        
        # Zero total_item_spend
        critical_items_7 = [{'supplier_spend': 100, 'total_item_spend': 0}]
        self.assertEqual(self.risk_calculator.calculate_single_sourcing_risk(critical_items_7), 0)

    def test_calculate_financial_health_risk(self):
        """Test the calculate_financial_health_risk method."""
        self.assertEqual(self.risk_calculator.calculate_financial_health_risk('High'), 25)
        self.assertEqual(self.risk_calculator.calculate_financial_health_risk('Medium'), 10)
        self.assertEqual(self.risk_calculator.calculate_financial_health_risk('Low'), 0)
        self.assertEqual(self.risk_calculator.calculate_financial_health_risk('Unknown'), 0)

    def test_calculate_spend_concentration_risk(self):
        """Test the calculate_spend_concentration_risk method."""
        # High concentration
        self.assertEqual(self.risk_calculator.calculate_spend_concentration_risk(250000), 20)
        self.assertEqual(self.risk_calculator.calculate_spend_concentration_risk(200000), 20)

        # Medium concentration
        self.assertEqual(self.risk_calculator.calculate_spend_concentration_risk(150000), 10)
        self.assertEqual(self.risk_calculator.calculate_spend_concentration_risk(100000), 10)

        # Low concentration
        self.assertEqual(self.risk_calculator.calculate_spend_concentration_risk(50000), 0)
        self.assertEqual(self.risk_calculator.calculate_spend_concentration_risk(0), 0)
        
        # Test with zero company total spend
        zero_spend_calculator = RiskCalculator({}, 0)
        self.assertEqual(zero_spend_calculator.calculate_spend_concentration_risk(50000), 0)

    def test_calculate_supplier_risk(self):
        """Test the calculate_supplier_risk method for total score and breakdown."""
        supplier_data_1 = {
            'country': 'HighRiskCountry',
            'financial_health_status': 'Medium',
            'total_spend': 150000,
            'critical_items': [{'supplier_spend': 95, 'total_item_spend': 100}]
        }
        
        expected_risk_1 = {
            'country_risk': 30,
            'single_sourcing_risk': 25,
            'financial_health_risk': 10,
            'spend_concentration_risk': 10,
            'total_risk': 75
        }
        self.assertEqual(self.risk_calculator.calculate_supplier_risk(supplier_data_1), expected_risk_1)

        # Test risk capping at 100
        supplier_data_2 = {
            'country': 'HighRiskCountry',
            'financial_health_status': 'High',
            'total_spend': 300000,
            'critical_items': [
                {'supplier_spend': 100, 'total_item_spend': 100},
                {'supplier_spend': 100, 'total_item_spend': 100},
                {'supplier_spend': 100, 'total_item_spend': 100},
                 {'supplier_spend': 100, 'total_item_spend': 100}
            ]
        }
        
        # without capping total risk would be: 30(country) + 25+15+15+15(single_sourcing) + 25(financial) + 20(spend) = 145
        risk_scores = self.risk_calculator.calculate_supplier_risk(supplier_data_2)
        self.assertEqual(risk_scores['total_risk'], 100)

if __name__ == '__main__':
    unittest.main()
