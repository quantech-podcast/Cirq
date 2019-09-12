# Copyright 2018 The Cirq Developers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Defines which types are Sweepable."""

from typing import cast, Iterable, Iterator, List, Union

from cirq.study.resolver import ParamResolver, ParamResolverOrSimilarType
from cirq.study.sweeps import ListSweep, Points, Sweep, UnitSweep, Zip


Sweepable = Union[
    ParamResolver, Iterable[ParamResolver], Sweep, Iterable[Sweep], None]


def to_resolvers(sweepable: Sweepable) -> Iterator[ParamResolver]:
    """Convert a Sweepable to a list of ParamResolvers."""
    if sweepable is None:
        yield ParamResolver({})
    elif isinstance(sweepable, ParamResolver):
        yield sweepable
    elif isinstance(sweepable, Sweep):
        for params in sweepable:
            yield params
    elif isinstance(sweepable, Iterable):
        for sub_sweepable in cast(Iterable, sweepable):
            yield from to_resolvers(sub_sweepable)
    else:
        raise TypeError('Unexpected Sweepable: {}'.format(sweepable))


def to_sweeps(sweepable: Sweepable) -> List[Sweep]:
    """Converts a Sweepable to a list of Sweeps."""
    if sweepable is None:
        return [UnitSweep]
    if isinstance(sweepable, ParamResolver):
        return [_resolver_to_sweep(sweepable)]
    if isinstance(sweepable, Sweep):
        return [sweepable]
    if isinstance(sweepable, Iterable):
        items = list(sweepable)
        if all(isinstance(item, Sweep) for item in items):
            return cast(List[Sweep], items)
        elif all(isinstance(item, ParamResolver) for item in items):
            return [_resolver_to_sweep(cast(ParamResolver, p)) for p in items]
    raise TypeError('Unexpected Sweepable: {}'.format(sweepable))


def to_sweep(sweep_or_resolver_list: Union['Sweep', ParamResolverOrSimilarType,
                                           Iterable[ParamResolverOrSimilarType]]
            ) -> 'Sweep':
    """Converts the argument into a `Sweep`.

    Args:
        sweep_or_resolver_list: The object to try to turn into a `Sweep`.  A
            `Sweep`, a single `ParamResolver`, or a list of `ParamResolver`s.

    Returns:
        A sweep equal to or containing the argument.
    """
    if isinstance(sweep_or_resolver_list, Sweep):
        return sweep_or_resolver_list
    if isinstance(sweep_or_resolver_list, (ParamResolver, dict)):
        resolver = cast(ParamResolverOrSimilarType, sweep_or_resolver_list)
        return ListSweep([resolver])
    if isinstance(sweep_or_resolver_list, Iterable):
        resolver_iter = cast(Iterable[ParamResolverOrSimilarType],
                             sweep_or_resolver_list)
        return ListSweep(resolver_iter)
    raise TypeError(
        'Unexpected sweep-like value: {}'.format(sweep_or_resolver_list))


def _resolver_to_sweep(resolver: ParamResolver) -> Sweep:
    params = resolver.param_dict
    if not params:
        return UnitSweep
    return Zip(
        *[Points(key, [cast(float, value)]) for key, value in params.items()])
