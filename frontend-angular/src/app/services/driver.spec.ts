import { TestBed } from '@angular/core/testing';

import { Driver } from './driver';

describe('Driver', () => {
  let service: Driver;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Driver);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
