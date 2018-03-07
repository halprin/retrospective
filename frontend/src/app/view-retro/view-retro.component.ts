import { Component, OnInit } from '@angular/core';
import { RetrospectiveService } from '../retrospective.service'

@Component({
  selector: 'app-view-retro',
  templateUrl: './view-retro.component.html',
  styleUrls: ['./view-retro.component.css']
})
export class ViewRetroComponent implements OnInit {
  name = 'Loading'

  constructor(private retroService: RetrospectiveService) { }

  ngOnInit() {
    this.retroService.getRetrospective().subscribe(json => this.name = json.name);
  }
}
