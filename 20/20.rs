use std::{
    cmp,
    collections::{HashMap, VecDeque},
    hash::Hash,
    io::{self, stdin},
};

use enum_map::{Enum, EnumMap};

#[derive(Clone)]
struct Machine<'a> {
    modules: HashMap<&'a str, Module<'a>>,
    input_modules: HashMap<&'a str, Vec<&'a str>>,
}

impl<'a> Machine<'a> {
    fn new(mut modules: HashMap<&'a str, Module<'a>>) -> Self {
        let mut input_modules = HashMap::<&str, Vec<&str>>::new();
        for name in modules.keys() {
            input_modules.insert(name, Vec::new());
        }
        for (name, module) in modules.iter() {
            for dest in &module.destinations {
                input_modules.entry(dest).or_default().push(name);
            }
        }
        for (name, module) in modules.iter_mut() {
            if let ModuleKind::Nand(ref mut remembered_pulses) = module.kind {
                remembered_pulses.resize(input_modules[name].len(), Pulse::Low);
            }
        }
        Self {
            modules,
            input_modules,
        }
    }

    fn send_pulse(&mut self, pulse: Pulse, target: &'a str) -> EnumMap<Pulse, u64> {
        let mut queue = VecDeque::new();
        queue.push_back((pulse, "button", target));

        let mut pulse_counts = EnumMap::default();

        while let Some((pulse, source, target)) = queue.pop_front() {
            pulse_counts[pulse] += 1;
            if let Some(module) = self.modules.get_mut(target) {
                if let Some(output_pulse) =
                    module.receive(source, pulse, &self.input_modules[target])
                {
                    for destination in &module.destinations {
                        queue.push_back((output_pulse, target, destination));
                    }
                }
            }
        }

        pulse_counts
    }

    fn sccs(&self) -> Vec<Vec<&str>> {
        let vertices = self.modules.keys().copied();
        let iterate_neighbors = |vertex| {
            self.modules
                .get(vertex)
                .map(|module| module.destinations.iter().copied())
                .unwrap_or_default()
        };
        sccs(vertices, iterate_neighbors)
    }
}

#[derive(Clone, PartialEq, Eq, Hash)]
struct Module<'a> {
    name: &'a str,
    destinations: Vec<&'a str>,
    kind: ModuleKind,
}

impl<'a> Module<'a> {
    fn receive(&mut self, source: &'a str, pulse: Pulse, input_modules: &[&str]) -> Option<Pulse> {
        match self.kind {
            ModuleKind::Broadcast => Some(pulse),
            ModuleKind::FlipFlop(ref mut state) => (pulse == Pulse::Low).then(|| {
                *state = state.inverse();
                *state
            }),
            ModuleKind::Nand(ref mut remembered_pulses) => {
                let index = input_modules
                    .iter()
                    .position(|&name| name == source)
                    .unwrap();
                remembered_pulses[index] = pulse;
                let all_high = remembered_pulses.iter().all(|&p| p == Pulse::High);

                Some(if all_high { Pulse::Low } else { Pulse::High })
            }
        }
    }
}

#[derive(Clone, PartialEq, Eq, Hash)]
enum ModuleKind {
    Broadcast,
    FlipFlop(Pulse),
    Nand(Vec<Pulse>),
}

#[derive(Debug, Clone, Copy, Enum, PartialEq, Eq, Hash)]
enum Pulse {
    Low,
    High,
}
impl Pulse {
    fn inverse(self) -> Self {
        match self {
            Pulse::Low => Pulse::High,
            Pulse::High => Pulse::Low,
        }
    }
}

fn sccs<V, F, N>(vertices: impl IntoIterator<Item = V>, iterate_neighbors: F) -> Vec<Vec<V>>
where
    V: Copy + Eq + Hash,
    F: Fn(V) -> N,
    N: IntoIterator<Item = V>,
{
    let mut sccs = Vec::new();
    let mut time = 0;
    let mut disc = HashMap::new();
    let mut stack = Vec::new();

    fn dfs<V, F, N>(
        v: V,
        iterate_neighbors: &F,
        time: &mut usize,
        disc: &mut HashMap<V, usize>,
        stack: &mut Vec<V>,
        sccs: &mut Vec<Vec<V>>,
    ) -> usize
    where
        V: Copy + Eq + Hash,
        F: Fn(V) -> N,
        N: IntoIterator<Item = V>,
    {
        let old_size = stack.len();
        stack.push(v);
        disc.insert(v, *time);
        let mut low = *time;
        *time += 1;
        for dest in iterate_neighbors(v) {
            if !disc.contains_key(&dest) {
                low = cmp::min(low, dfs(dest, iterate_neighbors, time, disc, stack, sccs));
            } else if stack.contains(&dest) {
                low = cmp::min(low, disc[&dest]);
            }
        }

        if low == disc[&v] {
            sccs.push(stack.drain(old_size..).collect());
        }
        low
    }

    for v in vertices {
        if !disc.contains_key(&v) {
            dfs(
                v,
                &iterate_neighbors,
                &mut time,
                &mut disc,
                &mut stack,
                &mut sccs,
            );
        }
    }

    sccs
}

fn part1(mut machine: Machine<'_>) -> u64 {
    let mut total_counts = EnumMap::<Pulse, u64>::default();
    for _ in 0..1000 {
        let counts = machine.send_pulse(Pulse::Low, "broadcaster");
        for (pulse, count) in counts.into_iter() {
            total_counts[pulse] += count;
        }
    }
    total_counts[Pulse::Low] * total_counts[Pulse::High]
}

fn part2(machine: Machine<'_>) -> u64 {
    // Solved by hand:
    //
    // The rx module has only one input, the dr module, which is a Nand module with four inputs. I
    // figured that there is some periodicity in the input button presses, but just finding the
    // period of the entire machine would take at least as long as running until the wanted signal
    // is sent (otherwise, it would never happen). So instead, I would look at the strongly
    // connected components:

    let sccs = dbg!(machine.sccs());

    // One could then probably partition the machine into sub-machines corresponding to the SCCs
    // and record the period and when pulses are sent between sub-machines. However, one thing that
    // is annoying then is that the pulses between machines could also happen while there are still
    // pulses in the queue of the sub-machine. I thought that this could maybe just not happen with
    // the input, but I wanted to verify it before starting to implement.

    // So I investigated the input a bit closer and had another idea: Since dr and rx are each
    // their own single-vertex-SCC, I would really just have to find out the period of each of the
    // input SCCs for dr.

    assert!(sccs.contains(&vec!["dr"]));
    assert!(sccs.contains(&vec!["rx"]));

    // Remembering day 8, the pattern is probably very nice, so it is likely that I can just make
    // an educated guess after looking at the pattern. Using the code from part 1, modified to loop
    // for 20_000 button presses and printing the iteration together with whenever the inputs of dr
    // change:
    //
    //     if self.name == "dr"
    //         && (pulse == Pulse::High || remembered_pulses[index] == Pulse::High)
    //     {
    //         eprintln!("{} {:?}", index, pulse);
    //     }
    //
    // shows that each input always turns Low after turning High in the same iteration and the
    // indices at which this happens are:
    //
    //     0: 4006 8013 12020 16027        => k * 4007 - 1
    //     1: 3916 7833 11750 15667 19584  => k * 3917 - 1
    //     2: 3918 7837 11756 15675 19594  => k * 3919 - 1
    //     3: 4026 8053 12080 16107        => k * 4027 - 1
    //
    // Since the iteration numbers are 0-based, all of them should actually be shifted by one. A
    // quick check with `factor` reveals that all of the numbers in the last column above are
    // prime, so this seems like we are on the right track. If the pattern continues, the first
    // iteration in which all inputs turn High at some point would be the lowest common multiple of
    // the periods, and well: Submitting the lcm (which, for primes, is the product) as an educated
    // guess is in fact the correct answer.
    //
    // (Luckily, it seems that the input is designed to do exactly that. In general, I think that
    // even though the inputs have these periods, it could be that in an iteration where they all
    // turn High, these Highs could be non-overlapping. Fortunately, this does not happen here.)

    4007 * 3917 * 3919 * 4027
}

fn main() {
    let input = io::read_to_string(stdin().lock()).expect("Failed to read stdin.");
    let mut modules = HashMap::new();

    for line in input.lines() {
        let (ident, destinations) = line.split_once(" -> ").unwrap();
        let destinations = destinations.split(", ").collect();
        let (kind, name) = if ident.starts_with('%') {
            (
                ModuleKind::FlipFlop(Pulse::Low),
                ident.trim_start_matches('%'),
            )
        } else if ident.starts_with('&') {
            (ModuleKind::Nand(Vec::new()), ident.trim_start_matches('&'))
        } else {
            (ModuleKind::Broadcast, ident)
        };

        modules.insert(
            name,
            Module {
                name,
                destinations,
                kind,
            },
        );
    }

    let machine = Machine::new(modules);
    println!("{}", part1(machine.clone()));
    println!("{}", part2(machine.clone()));
}
