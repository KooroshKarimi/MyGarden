# MyGarden - Python Garden Management

MyGarden is a lightweight Python library designed to help you manage your garden. It allows you to track your plants, record fertilization events, and determine when your plants need nutrients based on customizable intervals.

## Features

- **Plant Management**: Add plants with specific fertilization intervals (default: 30 days).
- **Fertilization Tracking**: Record when, what, and how much fertilizer was applied.
- **Smart Recommendations**: Check if a plant needs fertilizer based on its history and interval.
- **History**: Retrieve the full fertilization history for the entire garden or specific plants.
- **Persistence**: Save and load your garden data to/from a JSON file.

## Installation

This project requires Python 3.6+.

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/MyGarden.git
   cd MyGarden
   ```

2. Install dependencies (for testing):
   ```bash
   pip install pytest
   ```

## Usage

Here is a quick example of how to use MyGarden:

```python
from garden import Garden

# Initialize the garden
my_garden = Garden()

# Add plants
my_garden.add_plant("Rose", fertilizer_interval_days=14)
my_garden.add_plant("Cactus", fertilizer_interval_days=60)

# Check if they need fertilizer (initially, yes)
if my_garden.needs_fertilizer("Rose"):
    print("Rose needs fertilizer!")
    # Fertilize the plant
    my_garden.fertilize_plant("Rose", "RoseFood", 10.0)
    print("Rose fertilized.")

# Check again
if not my_garden.needs_fertilizer("Rose"):
    print("Rose is happy for now.")

# Save data
my_garden.save_to_file("my_garden_data.json")
```

## Running Tests

To ensure everything is working correctly, run the test suite using `pytest`:

```bash
pytest
```

## Project Structure

- `garden.py`: Core logic for the Garden class.
- `test_garden.py`: Unit tests ensuring reliability.
- `SPEZIFIKATION.md`: (Legacy/Context) Specifications for a related web project.

## License

MIT
