import { Component, OnInit } from '@angular/core';
import { RetrospectiveService } from '../retrospective.service'

@Component({
  selector: 'app-view-retro',
  templateUrl: './view-retro.component.html',
  styleUrls: ['./view-retro.component.css']
})
export class ViewRetroComponent implements OnInit {

  retro;

  constructor(private retroService: RetrospectiveService) { }

  ngOnInit() {
    this.retroService.startRetrospective('Sprint 26 Retrospective', 'Peter Kendall').subscribe(uuid => {
      this.retroService.getRetrospective().subscribe(json => this.retro = json);
    });
  }
}
