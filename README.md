# Factline

Factline is ...

## Usage
```bash
python3 main.py --input sample_input.json
```

## Tests
```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

## Input
```
{
  "hub_input_items": ["copper-plate", "iron-plate"],
  "hub_output_item": "electronic-circuit",
  "box_output_items": [],
  "machines": [
    {
      "kind": "ASSEMBLER_3X3",
      "count": 1,
      "input_items": ["copper-plate"],
      "output_item": "copper-cable"
    },
    {
      "kind": "ASSEMBLER_3X3",
      "count": 1,
      "input_items": ["iron-plate", "copper-cable"],
      "output_item": "electronic-circuit"
    }
  ]
}
```

## Output

```
height=3
width=7
machine_top=0
BIMMM  
BIMMMIB
BIMMM  
```
