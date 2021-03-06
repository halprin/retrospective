import { Component, OnInit, OnDestroy } from '@angular/core';
import { RetrospectiveServiceV2 } from '../retrospectiveV2.service';
import { environment } from '../../environments/environment';
import {Subscription} from 'rxjs';
import {ActivatedRoute} from '@angular/router';

@Component({
  selector: 'app-view-retro',
  templateUrl: './view-retro.component.html',
  styleUrls: ['./view-retro.component.css']
})
export class ViewRetroComponent implements OnInit, OnDestroy {

  retro: any;
  votes = 3;
  frontendEndpoint = environment.frontendEndpoint;
  private liveUpdater: Subscription;

  errorText = '';

  readySpinner = false;
  backSpinner = false;
  forwardSpinner = false;
  addGoodIssueSpinner = false;
  addBadIssueSpinner = false;
  deleteIssueSpinners = {};
  addGoodGroupSpinner = false;
  addBadGroupSpinner = false;
  deleteGroupSpinners = {};
  assignGroupSpinners = {};
  voteSpinners = {};

  constructor(private route: ActivatedRoute, private retroService: RetrospectiveServiceV2) { }

  ngOnInit() {
    if (!this.retroService.isRetrospectiveInitiated()) {
      // we got here through a refresh of the view page or basically not through the normal join
      const routeRetroId = this.route.snapshot.paramMap.get('id');
      const token = sessionStorage.getItem(`/retro/${routeRetroId}/token`);
      this.retroService.rejoinRetrospective(routeRetroId, token);
    }
    this.updateRetro();
    this.setupLiveUpdater();
  }

  setupLiveUpdater() {
    console.log('Setting-up the live updater');
    this.liveUpdater = this.retroService.startLiveUpdateRetrospective().subscribe(messageEvent => this.retro = JSON.parse(messageEvent.data), error => {
      const errorString = `Live updater failed to connect.  ${JSON.stringify(error)}`;
      this.errorText = errorString;
      console.error(errorString);
      setTimeout(() => { this.setupLiveUpdater(); }, 60000);
    }, () => {
      console.log('Complete live updater');
      this.setupLiveUpdater();
    });
  }

  ngOnDestroy() {
    this.liveUpdater.unsubscribe();
  }

  updateRetro(): void {
    this.retroService.getRetrospective().subscribe(json => this.retro = json, error => {
      const errorString = `Failed to get latest update of retrospective.  ${JSON.stringify(error)}`;
      this.errorText = errorString;
      console.error(errorString);
    });
  }

  alternateReadiness(): void {
    this.readySpinner = true;
    if (this.retro.yourself.ready === true) {
      this.retroService.markUserAsNotReady().subscribe(() => this.readySpinner = false, (error) => {
        this.readySpinner = false;
        const errorString = `Failed to mark you as NOT ready.  ${JSON.stringify(error)}`;
        this.errorText = errorString;
        console.error(errorString);
      }, () => this.readySpinner = false);
    } else {
      this.retroService.markUserAsReady().subscribe(() => this.readySpinner = false, (error) => {
        this.readySpinner = false;
        const errorString = `Failed to mark you as ready.  ${JSON.stringify(error)}`;
        this.errorText = errorString;
        console.error(errorString);
      }, () => this.readySpinner = false);
    }
  }

  addWentWellIssue(title: string): void {
    this.addGoodIssueSpinner = true;
    this.retroService.addIssue(title, 'Went Well').subscribe(() => this.addGoodIssueSpinner = false, (error) => {
      this.addGoodIssueSpinner = false;
      const errorString = `Failed to add a Went Well item.  ${JSON.stringify(error)}`;
      this.errorText = errorString;
      console.error(errorString);
    }, () => this.addGoodIssueSpinner = false);
  }

  addNeedsImprovementIssue(title: string): void {
    this.addBadIssueSpinner = true;
    this.retroService.addIssue(title, 'Needs Improvement').subscribe(() => this.addBadIssueSpinner = false, (error) => {
      this.addBadIssueSpinner = false;
      const errorString = `Failed to add a Needs Improvement issue.  ${JSON.stringify(error)}`;
      this.errorText = errorString;
      console.error(errorString);
    }, () => this.addBadIssueSpinner = false);
  }

  deleteIssue(issue_id: string): void {
    this.deleteIssueSpinners[issue_id] = true;
    this.retroService.deleteIssue(issue_id).subscribe(() => this.deleteIssueSpinners[issue_id] = false, (error) => {
      this.deleteIssueSpinners[issue_id] = false;
      const errorString = `Failed to delete an issue.  ${JSON.stringify(error)}`;
      this.errorText = errorString;
      console.error(errorString);
    }, () => this.deleteIssueSpinners[issue_id] = false);
  }

  getWentWellIssues(): any {
    const goodIssues = [];
    for (const issue of this.retro.issues) {
      if (issue.section === 'Went Well') {
        goodIssues.push(issue);
      }
    }

    return goodIssues;
  }

  getWentWellIssuesForGroup(group: string): any {
    const goodIssues = [];
    for (const issue of this.retro.issues) {
      if (issue.section === 'Went Well' && issue.group === group) {
        goodIssues.push(issue);
      }
    }

    return goodIssues;
  }

  getNeedsImprovementIssues(): any {
    const badIssues = [];
    for (const issue of this.retro.issues) {
      if (issue.section === 'Needs Improvement') {
        badIssues.push(issue);
      }
    }

    return badIssues;
  }

  getNeedsImprovementIssuesForGroup(group: string): any {
    const badIssues = [];
    for (const issue of this.retro.issues) {
      if (issue.section === 'Needs Improvement' && issue.group === group) {
        badIssues.push(issue);
      }
    }

    return badIssues;
  }

  issueTitle(issue: string): string {
    if (issue === undefined) {
      return '...';
    }

    return issue;
  }

  moveRetroBackward(): void {
    this.backSpinner = true;
    this.retroService.moveRetrospectiveBackward().subscribe(() => this.backSpinner = false, (error) => {
      this.backSpinner = false;
      const errorString = `Failed move retro back a step.  ${JSON.stringify(error)}`;
      this.errorText = errorString;
      console.error(errorString);
    }, () => this.backSpinner = false);
  }

  moveRetroForward(): void {
    this.forwardSpinner = true;
    this.retroService.moveRetrospectiveForward().subscribe(() => this.forwardSpinner = false, (error) => {
      this.forwardSpinner = false;
      const errorString = `Failed to move retro forward a step.  ${JSON.stringify(error)}`;
      this.errorText = errorString;
      console.error(errorString);
    }, () => this.forwardSpinner = false);
  }

  voteOrUnvoteForIssue(issue: any, checkbox: HTMLInputElement): void {
    if (checkbox.checked) {
      this.actuallyVoteForIssue(issue);
    } else {
      this.actuallyUnvoteForIssue(issue);
    }
  }

  voteOrUnvoteForGroup(group: any, checkbox: HTMLInputElement): void {
    if (checkbox.checked) {
      this.actuallyVoteForGroup(group);
    } else {
      this.actuallyUnvoteForGroup(group);
    }
  }

  addWentWellGroup(title: string): void {
    this.addGoodGroupSpinner = true;
    this.retroService.addGroup(title, 'Went Well').subscribe(() => this.addGoodGroupSpinner = false, (error) => {
      this.addGoodGroupSpinner = false;
      const errorString = `Failed to add a Went Well group.  ${JSON.stringify(error)}`;
      this.errorText = errorString;
      console.error(errorString);
    }, () => this.addGoodGroupSpinner = false);
  }

  addNeedsImprovementGroup(title: string): void {
    this.addBadGroupSpinner = true;
    this.retroService.addGroup(title, 'Needs Improvement').subscribe(() => this.addBadGroupSpinner = false, (error) => {
      this.addBadGroupSpinner = false;
      const errorString = `Failed to add a Needs Improvement group.  ${JSON.stringify(error)}`;
      this.errorText = errorString;
      console.error(errorString);
    }, () => this.addBadGroupSpinner = false);
  }

  deleteGroup(group_id: string): void {
    this.deleteGroupSpinners[group_id] = true;
    this.retroService.deleteGroup(group_id).subscribe(() => this.deleteGroupSpinners[group_id] = false, (error) => {
      this.deleteGroupSpinners[group_id] = false;
      const errorString = `Failed to delete a group.  ${JSON.stringify(error)}`;
      this.errorText = errorString;
      console.error(errorString);
    }, () => this.deleteGroupSpinners[group_id] = false);
  }

  getWentWellGroups(): any {
    const goodGroups = [];
    for (const group of this.retro.groups) {
      if (group.section === 'Went Well') {
        goodGroups.push(group);
      }
    }

    return goodGroups;
  }

  getNeedsImprovementGroups(): any {
    const badGroups = [];
    for (const group of this.retro.groups) {
      if (group.section === 'Needs Improvement') {
        badGroups.push(group);
      }
    }

    return badGroups;
  }

  groupOrUngroupIssue(issue_id: string, group_id: string): void {
    this.assignGroupSpinners[issue_id] = true;
    if (group_id === 'ungroup') {
      this.retroService.ungroupIssue(issue_id).subscribe(() => this.assignGroupSpinners[issue_id] = false, (error) => {
        this.assignGroupSpinners[issue_id] = false;
        const errorString = `Failed to UNgroup an issue.  ${JSON.stringify(error)}`;
        this.errorText = errorString;
        console.error(errorString);
      }, () => this.assignGroupSpinners[issue_id] = false);
    } else {
      this.retroService.groupIssue(issue_id, group_id).subscribe(() => this.assignGroupSpinners[issue_id] = false, (error) => {
        this.assignGroupSpinners[issue_id] = false;
        const errorString = `Failed to group an issue.  ${JSON.stringify(error)}`;
        this.errorText = errorString;
        console.error(errorString);
      }, () => this.assignGroupSpinners[issue_id] = false);
    }
  }

  isIssueGroupedWithGroup(issue_id: string, group_id: string): boolean {
    for (const issue of this.retro.issues) {
      if (issue.id === issue_id) {
        return (issue.group === group_id);
      }
    }
  }

  isIssueUngrouped(issue_id: string): boolean {
    for (const issue of this.retro.issues) {
      if (issue.id === issue_id) {
        return (issue.group === null);
      }
    }
  }

  hideError(): void {
    this.errorText = '';
  }

  private actuallyVoteForIssue(issue: any): void {
    const issue_id = issue.id;
    this.voteSpinners[issue_id] = true;
    this.simulateVoteForIssueOrGroup(issue);
    this.retroService.voteForIssue(issue_id).subscribe(response => this.voteSpinners[issue_id] = false, error => {
      this.simulateUnvoteForIssueOrGroup(issue);
      this.voteSpinners[issue_id] = false;
      const errorString = `Failed to vote for an issue.  ${JSON.stringify(error)}`;
      this.errorText = errorString;
      console.error(errorString);
    });
  }

  private actuallyUnvoteForIssue(issue: any): void {
    const issue_id = issue.id;
    this.voteSpinners[issue_id] = true;
    this.simulateUnvoteForIssueOrGroup(issue);
    this.retroService.unvoteForIssue(issue_id).subscribe(response => this.voteSpinners[issue_id] = false, error => {
      this.simulateVoteForIssueOrGroup(issue);
      this.voteSpinners[issue_id] = false;
      const errorString = `Failed to UNvote for an issue.  ${JSON.stringify(error)}`;
      this.errorText = errorString;
      console.error(errorString);
    });
  }

  private actuallyVoteForGroup(group: any): void {
    const group_id = group.id;
    this.voteSpinners[group_id] = true;
    this.simulateVoteForIssueOrGroup(group);
    this.retroService.voteForGroup(group_id).subscribe(response => this.voteSpinners[group_id] = false, error => {
      this.simulateUnvoteForIssueOrGroup(group);
      this.voteSpinners[group_id] = false;
      const errorString = `Failed to vote for a group.  ${JSON.stringify(error)}`;
      this.errorText = errorString;
      console.error(errorString);
    });
  }

  private actuallyUnvoteForGroup(group: any): void {
    const group_id = group.id;
    this.voteSpinners[group_id] = true;
    this.simulateUnvoteForIssueOrGroup(group);
    this.retroService.unvoteForGroup(group_id).subscribe(response => this.voteSpinners[group_id] = false, error => {
      this.simulateVoteForIssueOrGroup(group);
      this.voteSpinners[group_id] = false;
      const errorString = `Failed to UNvote for a group.  ${JSON.stringify(error)}`;
      this.errorText = errorString;
      console.error(errorString);
    });
  }

  private simulateVoteForIssueOrGroup(issue_or_group: any) {
    this.votes--;
    issue_or_group.votes = 1;
  }

  private simulateUnvoteForIssueOrGroup(issue_or_group: any) {
    this.votes++;
    issue_or_group.votes = 0;
  }
}
