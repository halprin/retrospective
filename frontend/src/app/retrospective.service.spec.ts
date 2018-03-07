import { TestBed, inject } from '@angular/core/testing';

import { RetrospectiveService } from './retrospective.service';

describe('RetrospectiveService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [RetrospectiveService]
    });
  });

  it('should be created', inject([RetrospectiveService], (service: RetrospectiveService) => {
    expect(service).toBeTruthy();
  }));
});
