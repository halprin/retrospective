import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { RetrospectiveService } from '../retrospective.service'

@Component({
  selector: 'app-start-retro',
  templateUrl: './start-retro.component.html',
  styleUrls: ['./start-retro.component.css']
})
export class StartRetroComponent implements OnInit {

  constructor(private router: Router, private retroService: RetrospectiveService) { }

  ngOnInit() {
  }

  startRetro(retroName: string, userName: string): void {
    this.retroService.startRetrospective(retroName, userName)
      .subscribe(uuid => {
        this.router.navigateByUrl('/view');
      });
  }
}
