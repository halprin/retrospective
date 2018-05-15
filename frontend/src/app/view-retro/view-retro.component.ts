import { Component, OnInit, OnDestroy } from '@angular/core';
import { RetrospectiveService } from '../retrospective.service'
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

  constructor(private retroService: RetrospectiveService) { }

  ngOnInit() {
    this.updateRetro();
    this.liveUpdater = this.retroService.startLiveUpdateRetrospective().subscribe(messageEvent => this.retro = JSON.parse(messageEvent.data));
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
      if(issue.section == 'Went Well') {
        goodIssues.push(issue);
      }
    }

    return goodIssues;
  }

  getNeedsImprovementIssues(): any {
    let badIssues = [];
    for(let issue of this.retro.issues) {
      if(issue.section == 'Needs Improvement') {
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

  private actuallyVoteForIssue(issue: any): void {
    let issue_id = issue.id;
    this.simulateVoteForIssue(issue);
    this.retroService.voteForIssue(issue_id).subscribe(response => {}, error => {
      this.simulateUnvoteForIssue(issue);
    });
  }

  private actuallyUnvoteForIssue(issue: any): void {
    let issue_id = issue.id;
    this.simulateUnvoteForIssue(issue);
    this.retroService.unvoteForIssue(issue_id).subscribe(response => {}, error => {
      this.simulateVoteForIssue(issue);
    });
  }

  private simulateVoteForIssue(issue: any) {
    this.votes--;
    issue.votes = 1;
  }

  private simulateUnvoteForIssue(issue: any) {
    this.votes++;
    issue.votes = 0;
  }
}
