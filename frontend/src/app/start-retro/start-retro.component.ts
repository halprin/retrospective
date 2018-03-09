import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { HttpErrorResponse} from '@angular/common/http'
import { RetrospectiveService } from '../retrospective.service'

@Component({
  selector: 'app-start-retro',
  templateUrl: './start-retro.component.html',
  styleUrls: ['./start-retro.component.css']
})
export class StartRetroComponent implements OnInit {

  errorText = '';

  constructor(private router: Router, private retroService: RetrospectiveService) { }

  ngOnInit() {
  }

  startRetro(retroName: string, userName: string): void {
    this.retroService.startRetrospective(retroName, userName)
      .subscribe(uuid => {
        this.router.navigateByUrl('/view');
      },
      (error: HttpErrorResponse) => {
        this.displayError('Something bad happened.  Please contact us with the following information: [Status - ' + error.status + ', Message - ' + error.message + ']');
      });
  }

  displayError(errorMessage: string): void {
    this.errorText = errorMessage;
  }

  hideError(): void {
    this.errorText = '';
  }
}
