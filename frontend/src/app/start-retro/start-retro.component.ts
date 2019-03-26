import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { HttpErrorResponse} from '@angular/common/http'
import { RetrospectiveServiceV2 } from '../retrospectiveV2.service'

@Component({
  selector: 'app-start-retro',
  templateUrl: './start-retro.component.html',
  styleUrls: ['./start-retro.component.css']
})
export class StartRetroComponent implements OnInit {

  errorText = '';
  startButtonText = 'Start';

  constructor(private router: Router, private retroService: RetrospectiveServiceV2) { }

  ngOnInit() {
  }

  startRetro(retroName: string, userName: string): void {
    this.startLoadingIndicator();
    this.retroService.startRetrospective(retroName, userName)
      .subscribe(uuid => {
        this.stopLoadingIndicator();
        this.router.navigateByUrl('/view');
      },
      (error: HttpErrorResponse) => {
        this.stopLoadingIndicator();
        this.displayError('Something bad happened.  Please contact us with the following information: [Status - ' + error.status + ', Message - ' + error.message + ']');
      });
  }

  startLoadingIndicator(): void {
    this.startButtonText = ' Starting...';
  }

  stopLoadingIndicator(): void {
    this.startButtonText = 'Start';
  }

  displayError(errorMessage: string): void {
    this.errorText = errorMessage;
  }

  hideError(): void {
    this.errorText = '';
  }
}
