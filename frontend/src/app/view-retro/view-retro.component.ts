import { Component, OnInit } from '@angular/core';
import { RetrospectiveService } from '../retrospective.service'
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-view-retro',
  templateUrl: './view-retro.component.html',
  styleUrls: ['./view-retro.component.css']
})
export class ViewRetroComponent implements OnInit {

  retro;
  votes = 3;
  frontendEndpoint = environment.frontendEndpoint;

  constructor(private retroService: RetrospectiveService) { }

  ngOnInit() {
    this.retroService.startRetrospective('Sprint 26 Retrospective', 'Peter Kendall').subscribe(uuid => {
      this.updateRetro();
    });
  }

  updateRetro(): void {
    this.retroService.getRetrospective().subscribe(json => this.retro = json);
  }

  alternateReadiness(): void {
    if (this.retro.yourself.ready == true) {
      this.retroService.markUserAsNotReady().subscribe(response => {
        this.updateRetro();
      });
    } else {
      this.retroService.markUserAsReady().subscribe(response => {
        this.updateRetro();
      });
    }
  }

  addWentWellIssue(title: string): void {
    this.retroService.addIssue(title, 'Went Well').subscribe(id => {
      this.updateRetro();
    });
  }

  addNeedsImprovementIssue(title: string): void {
    this.retroService.addIssue(title, 'Needs Improvement').subscribe(id => {
      this.updateRetro();
    });
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
    this.retroService.moveRetrospectiveBackward().subscribe(newStep => {
      this.updateRetro();
    });
  }

  moveRetroForward(): void {
    this.retroService.moveRetrospectiveForward().subscribe(newStep => {
      this.updateRetro();
    });
  }

  voteForIssue(issue_id: string, checkbox: any): void {
    this.votes--;
    this.retroService.voteForIssue(issue_id).subscribe(response => {
      this.updateRetro();
    }, error => {
      this.votes++;
      checkbox.checked = false;
    });
  }
}
