class RiskCalculator:
    def __init__(self, country_risk_map, company_total_spend):
        """
        Initializes the RiskCalculator with risk mappings and company total spend.

        Args:
            country_risk_map (dict): A map of countries to risk levels ('High Risk', 'Medium Risk', 'Low Risk').
            company_total_spend (float): The total spend of the company.
        """
        self.country_risk_map = country_risk_map
        self.company_total_spend = company_total_spend

    def calculate_country_risk(self, country):
        risk_level = self.country_risk_map.get(country, "Low Risk")
        if risk_level == "High Risk":
            return 30
        elif risk_level == "Medium Risk":
            return 15
        else:
            return 0

    def calculate_single_sourcing_risk(self, critical_items):
        """
        Calculates the single sourcing risk based on a list of critical items.

        Args:
            critical_items (list): A list of dictionaries, where each dictionary represents a critical item and has:
                - 'supplier_spend' (float)
                - 'total_item_spend' (float)
        """
        single_sourced_items = []
        partially_sourced_items = []

        for item in critical_items:
            if item['total_item_spend'] > 0:
                spend_percentage = (item['supplier_spend'] / item['total_item_spend']) * 100
                if spend_percentage >= 90:
                    single_sourced_items.append(item)
                elif 50 <= spend_percentage < 90:
                    partially_sourced_items.append(item)

        total_risk = 0
        if single_sourced_items:
            total_risk += 25  # First single-sourced item
            total_risk += (len(single_sourced_items) - 1) * 15  # Additional single-sourced items
            total_risk += len(partially_sourced_items) * 7.5  # All partially-sourced items
        elif partially_sourced_items:
            total_risk += 10  # First partially-sourced item
            total_risk += (len(partially_sourced_items) - 1) * 7.5  # Additional partially-sourced items
        
        return total_risk

    def calculate_financial_health_risk(self, financial_health_status):
        if financial_health_status == "Low":
            return 25
        elif financial_health_status == "Medium":
            return 10
        else:
            return 0

    def calculate_spend_concentration_risk(self, supplier_total_spend):
        if self.company_total_spend == 0:
            return 0
            
        spend_percentage = (supplier_total_spend / self.company_total_spend) * 100
        if spend_percentage >= 20:
            return 20
        elif 10 <= spend_percentage < 20:
            return 10
        else:
            return 0

    def calculate_supplier_risk(self, supplier_data):
        """
        Calculates the supplier risk based on supplier data.

        Args:
            supplier_data (dict): A dictionary containing supplier data including:
                - 'country' (str)
                - 'financial_health_status' (str)
                - 'total_spend' (float)
                - 'critical_items' (list of dicts): see calculate_single_sourcing_risk docstring.

        Returns:
            int: The calculated supplier risk score, capped at 100.
        """
        country_risk = self.calculate_country_risk(supplier_data["country"])
        
        single_sourcing_risk = self.calculate_single_sourcing_risk(supplier_data["critical_items"])

        financial_health_risk = self.calculate_financial_health_risk(supplier_data["financial_health_status"])
        
        spend_concentration_risk = self.calculate_spend_concentration_risk(supplier_data["total_spend"])

        total_risk = (
            country_risk +
            single_sourcing_risk +
            financial_health_risk +
            spend_concentration_risk
        )

        return min(total_risk, 100)
