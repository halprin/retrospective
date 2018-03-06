import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-start-retro',
  templateUrl: './start-retro.component.html',
  styleUrls: ['./start-retro.component.css']
})
export class StartRetroComponent implements OnInit {

  constructor(private router: Router) { }

  ngOnInit() {
  }

  start_retro(retro_name: string, user_name: string): void {
    this.router.navigateByUrl('/view');
  }
}
