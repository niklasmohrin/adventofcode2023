use std::{
    cmp,
    collections::HashMap,
    io::{self, stdin},
    ops::Range,
};

use enum_map::{enum_map, Enum, EnumMap};
use nom::{
    branch::alt,
    bytes::complete::tag,
    character::complete::{alpha1, i32, newline},
    combinator::{map, opt},
    multi::{many1, separated_list1},
    sequence::{delimited, pair, separated_pair, terminated, tuple},
    IResult,
};

#[derive(Clone, Copy, Enum)]
enum Property {
    ExtremelyCoolLooking,
    Musical,
    Aerodynamic,
    Shiny,
}

#[derive(Default)]
struct Part {
    properties: EnumMap<Property, i32>,
}

struct Workflow<'a> {
    name: &'a str,
    rules: Vec<Rule<'a>>,
}

impl<'a> Workflow<'a> {
    fn accepts(&self, part: &Part, workflows: &HashMap<&str, Self>) -> bool {
        for rule in &self.rules {
            if rule
                .condition
                .as_ref()
                .map_or(true, |cond| cond.holds_for(part))
            {
                return match rule.target {
                    "A" => true,
                    "R" => false,
                    target => workflows[target].accepts(part, workflows),
                };
            }
        }
        unreachable!()
    }

    fn possible_inputs_ranging(
        &self,
        mut property_ranges: EnumMap<Property, Range<i32>>,
        workflows: &HashMap<&str, Self>,
    ) -> u64 {
        let mut total = 0;
        let mut recurse = |ranges: EnumMap<Property, Range<i32>>, target| {
            total += match target {
                "A" => ranges.values().map(|range| range.len() as u64).product(),
                "R" => 0,
                _ => workflows[target].possible_inputs_ranging(ranges, workflows),
            }
        };

        for rule in &self.rules {
            if let Some(condition) = &rule.condition {
                let [true_ranges, false_ranges] = condition.split(property_ranges);
                recurse(true_ranges, rule.target);
                property_ranges = false_ranges;
            } else {
                recurse(property_ranges, rule.target);
                return total;
            }
        }

        unreachable!()
    }
}

struct Rule<'a> {
    condition: Option<Condition>,
    target: &'a str,
}

struct Condition {
    property: Property,
    admissible_values: Range<i32>,
}

impl Condition {
    fn holds_for(&self, part: &Part) -> bool {
        self.admissible_values
            .contains(&part.properties[self.property])
    }

    fn intersect(r1: &Range<i32>, r2: &Range<i32>) -> Range<i32> {
        let start = cmp::max(r1.start, r2.start);
        let end = cmp::max(start, cmp::min(r1.end, r2.end));
        start..end
    }

    fn inadmissible_values(&self) -> Range<i32> {
        if self.admissible_values.start == i32::MIN {
            self.admissible_values.end..i32::MAX
        } else {
            debug_assert_eq!(self.admissible_values.end, i32::MAX);
            i32::MIN..self.admissible_values.start
        }
    }

    fn split(&self, ranges: EnumMap<Property, Range<i32>>) -> [EnumMap<Property, Range<i32>>; 2] {
        let mut true_ranges = ranges.clone();
        let mut false_ranges = ranges;
        true_ranges[self.property] =
            Self::intersect(&true_ranges[self.property], &self.admissible_values);
        false_ranges[self.property] =
            Self::intersect(&false_ranges[self.property], &self.inadmissible_values());
        [true_ranges, false_ranges]
    }
}

fn parse_property(input: &str) -> IResult<&str, Property> {
    alt((
        map(tag("x"), |_| Property::ExtremelyCoolLooking),
        map(tag("m"), |_| Property::Musical),
        map(tag("a"), |_| Property::Aerodynamic),
        map(tag("s"), |_| Property::Shiny),
    ))(input)
}

fn parse_condition(input: &str) -> IResult<&str, Condition> {
    map(
        tuple((parse_property, alt((tag("<"), tag(">"))), i32)),
        |(property, relation, bound)| {
            let admissible_values = match relation {
                "<" => i32::MIN..bound,
                ">" => (bound + 1)..i32::MAX,
                _ => unreachable!(),
            };
            Condition {
                property,
                admissible_values,
            }
        },
    )(input)
}

fn parse_rule(input: &str) -> IResult<&str, Rule<'_>> {
    map(
        pair(opt(terminated(parse_condition, tag(":"))), alpha1),
        |(condition, target)| Rule { condition, target },
    )(input)
}

fn parse_workflow(input: &str) -> IResult<&str, Workflow<'_>> {
    map(
        pair(
            alpha1,
            delimited(tag("{"), separated_list1(tag(","), parse_rule), tag("}")),
        ),
        |(name, rules)| Workflow { name, rules },
    )(input)
}

fn parse_part(input: &str) -> IResult<&str, Part> {
    delimited(
        tag("{"),
        map(
            separated_list1(tag(","), separated_pair(parse_property, tag("="), i32)),
            |assignments| Part {
                properties: assignments.into_iter().collect(),
            },
        ),
        tag("}"),
    )(input)
}

fn main() {
    let input = io::read_to_string(stdin().lock()).expect("Failed to read stdin.");

    let mut parse_input = separated_pair(
        many1(terminated(parse_workflow, newline)),
        newline,
        many1(terminated(parse_part, newline)),
    );
    let (rest, (workflows, parts)) = parse_input(&input).expect("Failed to parse input.");
    assert!(rest.is_empty());

    let workflows_by_name: HashMap<&str, Workflow> = workflows
        .into_iter()
        .map(|workflow| (workflow.name, workflow))
        .collect();

    let part1: i32 = parts
        .into_iter()
        .filter(|part| workflows_by_name["in"].accepts(part, &workflows_by_name))
        .map(|part| part.properties.values().sum::<i32>())
        .sum();
    println!("{}", part1);

    let part2 = workflows_by_name["in"].possible_inputs_ranging(
        enum_map! {
            Property::ExtremelyCoolLooking => 1..4001,
            Property::Musical => 1..4001,
            Property::Aerodynamic => 1..4001,
            Property::Shiny => 1..4001,
        },
        &workflows_by_name,
    );
    println!("{}", part2);
}
