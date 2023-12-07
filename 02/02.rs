use std::io::{self, stdin};

use enum_map::{enum_map, Enum, EnumMap};
use nom::{
    branch::alt,
    bytes::complete::tag,
    character::complete::{newline, u32},
    combinator::map,
    multi::{many0, separated_list1},
    sequence::{pair, preceded, separated_pair, terminated},
    IResult,
};

#[derive(Debug, Clone, Copy, Enum)]
enum Color {
    Red,
    Green,
    Blue,
}

#[derive(Debug, Default)]
struct Draw {
    occurences: EnumMap<Color, u32>,
}

#[derive(Debug)]
struct Game {
    id: u32,
    draws: Vec<Draw>,
}

impl Game {
    fn min_needed(&self) -> EnumMap<Color, u32> {
        EnumMap::from_fn(|color| {
            self.draws
                .iter()
                .map(|draw| draw.occurences[color])
                .fold(0, u32::max)
        })
    }

    fn power(&self) -> u32 {
        self.min_needed().values().product()
    }
}

fn parse_color(input: &str) -> IResult<&str, Color> {
    alt((
        map(tag("red"), |_| Color::Red),
        map(tag("green"), |_| Color::Green),
        map(tag("blue"), |_| Color::Blue),
    ))(input)
}

fn parse_draw(input: &str) -> IResult<&str, Draw> {
    let (remainder, draw_data) =
        separated_list1(tag(", "), separated_pair(u32, tag(" "), parse_color))(input)?;
    let mut draw = Draw::default();
    for (count, color) in draw_data {
        draw.occurences[color] += count;
    }
    Ok((remainder, draw))
}

fn parse_game(input: &str) -> IResult<&str, Game> {
    let parse_id = preceded(tag("Game "), terminated(u32, tag(": ")));
    let parse_draws = separated_list1(tag("; "), parse_draw);
    let mut parse = map(pair(parse_id, parse_draws), |(id, draws)| Game {
        id,
        draws,
    });
    parse(input)
}

fn parse_input(input: &str) -> IResult<&str, Vec<Game>> {
    many0(terminated(parse_game, newline))(input)
}

fn main() {
    let input = io::read_to_string(stdin().lock()).expect("Failed to read stdin.");
    let (_, games) = parse_input(&input).expect("Failed to parse input.");

    let max_cubes = enum_map! {
        Color::Red => 12,
        Color::Green => 13,
        Color::Blue => 14,
    };

    let possible_with_max_cubes = games.iter().filter(|game| {
        game.draws.iter().all(|draw| {
            max_cubes
                .iter()
                .all(|(color, &count)| draw.occurences[color] <= count)
        })
    });
    let part1: u32 = possible_with_max_cubes.map(|game| game.id).sum();
    dbg!(part1);

    let part2: u32 = games.iter().map(Game::power).sum();
    dbg!(part2);
}
