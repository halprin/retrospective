from backend.api.modelsV2 import RetroStepV2
import pytest


previous_step_regex = 'No previous step before [a-zA-Z]+'
next_step_regex = 'No next step after [a-zA-Z]+'


def test_each_step():
    retro_steps = list(RetroStepV2)

    for index, retro_step in enumerate(retro_steps):
        if index == 0:
            with pytest.raises(ValueError, match=previous_step_regex):
                retro_step.previous()
            assert retro_step.next() == retro_steps[index + 1]

        elif index == len(retro_steps) - 1:
            assert retro_step.previous() == retro_steps[index - 1]
            with pytest.raises(ValueError, match=next_step_regex):
                retro_step.next()

        else:
            assert retro_step.previous() == retro_steps[index - 1]
            assert retro_step.next() == retro_steps[index + 1]


def test_grouping_after_adding_issues():
    assert RetroStepV2.ADDING_ISSUES.next() == RetroStepV2.GROUPING


def test_grouping_before_voting():
    assert RetroStepV2.VOTING.previous() == RetroStepV2.GROUPING
