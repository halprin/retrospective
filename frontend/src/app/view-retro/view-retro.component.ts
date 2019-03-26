import { Component, OnInit, OnDestroy } from '@angular/core';
import { RetrospectiveServiceV2 } from '../retrospectiveV2.service'
import { environment } from '../../environments/environment';
import 'rxjs/add/observable/interval';
import {Subscription} from "rxjs/Subscription";

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

  constructor(private retroService: RetrospectiveServiceV2) { }

  ngOnInit() {
    this.updateRetro();
    this.setupLiveUpdater();
  }

  setupLiveUpdater() {
    this.liveUpdater = this.retroService.startLiveUpdateRetrospective().subscribe(messageEvent => this.retro = JSON.parse(messageEvent.data), error => {
      console.error('Error on live updater');
      this.setupLiveUpdater();
    }, () => {
      console.info('Complete live updater');
      this.setupLiveUpdater();
    });
  }

  ngOnDestroy() {
    this.liveUpdater.unsubscribe();
  }

  updateRetro(): void {
    this.retroService.getRetrospective().subscribe(json => this.retro = json);
  }

  alternateReadiness(): void {
    if (this.retro.yourself.ready == true) {
      this.retroService.markUserAsNotReady().subscribe();
    } else {
      this.retroService.markUserAsReady().subscribe();
    }
  }

  addWentWellIssue(title: string): void {
    this.retroService.addIssue(title, 'Went Well').subscribe();
  }

  addNeedsImprovementIssue(title: string): void {
    this.retroService.addIssue(title, 'Needs Improvement').subscribe();
  }

  deleteIssue(issue_id: string): void {
    this.retroService.deleteIssue(issue_id).subscribe();
  }

  getWentWellIssues(): any {
    let goodIssues = [];
    for(let issue of this.retro.issues) {
      if(issue.section === 'Went Well') {
        goodIssues.push(issue);
      }
    }

    return goodIssues;
  }

  getWentWellIssuesForGroup(group: string): any {
    let goodIssues = [];
    for(let issue of this.retro.issues) {
      if(issue.section === 'Went Well' && issue.group === group) {
        goodIssues.push(issue);
      }
    }

    return goodIssues;
  }

  getNeedsImprovementIssues(): any {
    let badIssues = [];
    for(let issue of this.retro.issues) {
      if(issue.section === 'Needs Improvement') {
        badIssues.push(issue);
      }
    }

    return badIssues;
  }

  getNeedsImprovementIssuesForGroup(group: string): any {
    let badIssues = [];
    for(let issue of this.retro.issues) {
      if(issue.section === 'Needs Improvement' && issue.group === group) {
        badIssues.push(issue);
      }
    }

    return badIssues;
  }

  issueTitle(issue: string): string {
    if(issue == null) {
      return '...'
    }

    return issue;
  }

  moveRetroBackward(): void {
    this.retroService.moveRetrospectiveBackward().subscribe();
  }

  moveRetroForward(): void {
    this.retroService.moveRetrospectiveForward().subscribe();
  }

  voteOrUnvoteForIssue(issue: any, checkbox: HTMLInputElement): void {
    if(checkbox.checked) {
      this.actuallyVoteForIssue(issue)
    } else {
      this.actuallyUnvoteForIssue(issue)
    }
  }

  voteOrUnvoteForGroup(group: any, checkbox: HTMLInputElement): void {
    if(checkbox.checked) {
      this.actuallyVoteForGroup(group)
    } else {
      this.actuallyUnvoteForGroup(group)
    }
  }

  addWentWellGroup(title: string): void {
    this.retroService.addGroup(title, 'Went Well').subscribe();
  }

  addNeedsImprovementGroup(title: string): void {
    this.retroService.addGroup(title, 'Needs Improvement').subscribe();
  }

  deleteGroup(group_id: string): void {
    this.retroService.deleteGroup(group_id).subscribe();
  }

  getWentWellGroups(): any {
    let goodGroups = [];
    for(let group of this.retro.groups) {
      if(group.section === 'Went Well') {
        goodGroups.push(group);
      }
    }

    return goodGroups;
  }

  getNeedsImprovementGroups(): any {
    let badGroups = [];
    for(let group of this.retro.groups) {
      if(group.section === 'Needs Improvement') {
        badGroups.push(group);
      }
    }

    return badGroups;
  }

  groupOrUngroupIssue(issue_id: string, group_id: string): void {
    if(group_id === 'ungroup') {
      this.retroService.ungroupIssue(issue_id).subscribe();
    } else {
      this.retroService.groupIssue(issue_id, group_id).subscribe();
    }
  }

  isIssueGroupedWithGroup(issue_id: string, group_id: string): boolean {
    for(let issue of this.retro.issues) {
      if(issue.id === issue_id) {
        return (issue.group === group_id)
      }
    }
  }

  isIssueUngrouped(issue_id: string): boolean {
    for(let issue of this.retro.issues) {
      if(issue.id === issue_id) {
        return (issue.group === null)
      }
    }
  }

  private actuallyVoteForIssue(issue: any): void {
    let issue_id = issue.id;
    this.simulateVoteForIssueOrGroup(issue);
    this.retroService.voteForIssue(issue_id).subscribe(response => {}, error => {
      this.simulateUnvoteForIssueOrGroup(issue);
    });
  }

  private actuallyUnvoteForIssue(issue: any): void {
    let issue_id = issue.id;
    this.simulateUnvoteForIssueOrGroup(issue);
    this.retroService.unvoteForIssue(issue_id).subscribe(response => {}, error => {
      this.simulateVoteForIssueOrGroup(issue);
    });
  }

  private actuallyVoteForGroup(group: any): void {
    let group_id = group.id;
    this.simulateVoteForIssueOrGroup(group);
    this.retroService.voteForGroup(group_id).subscribe(response => {}, error => {
      this.simulateUnvoteForIssueOrGroup(group);
    });
  }

  private actuallyUnvoteForGroup(group: any): void {
    let group_id = group.id;
    this.simulateUnvoteForIssueOrGroup(group);
    this.retroService.unvoteForGroup(group_id).subscribe(response => {}, error => {
      this.simulateVoteForIssueOrGroup(group);
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
