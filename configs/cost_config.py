vehicle_cost = {
	"gasoline": {
		"Seat Leon 1.5 TSI 2020": {
			"leasing_cost": 3024,
			"maintainance_cost": 23,
			"cost_permin": 0.26
		},
	},
	"electric": {
		"Fiat 500e 2020": {
			"leasing_cost": 4000,
			"maintainance_cost": 6,
			"cost_permin": 0.26
		},
	}
}

charging_station_costs = {
	"single_phase_2": {
		"hardware": 3127,
		"labor": 1544,
		"materials": 1112,
		"permit": 82,
		"taxes": (22 / 100) * 3127,
		"government_subsidy": -1500
	},
	"pole_useful_life": 10
}

fuel_costs = {
	"gasoline": {
		"fuel_cost": 1.845,
		"lower_heating_value": 42.3,  # MJ/kg
		"density": 745.8  # g/L
	},
	"diesel": {
		"fuel_cost": 2.018,
		"lower_heating_value": 42.7,  # MJ/kg
		"density": 836.1  # g/L
	},
	"lpg": {
		"fuel_cost": 0.785,
		"lower_heating_value": 46,  # MJ/kg
		"density": 550  # g/L
	},
	"cng": {
		"fuel_cost": 0.975,
		"lower_heating_value": 48,  # MJ/kg
		"density": 1000  # g/L
	},
	"electric": {
		"fuel_cost": 0.2634,
		"charging_efficiency": 80
	}
}

administrative_cost_conf = {
	"relocation_workers_hourly_cost": 23,
}
