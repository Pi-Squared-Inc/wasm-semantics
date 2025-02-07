#[cfg(test)]
mod erc20_tests {
    use crate::address::Address;
    use crate::balance::Balance;
    use crate::erc20::*;
    use crate::ulm;
    use crate::unsigned::*;

    fn balance(value: u64) -> Balance {
        Balance::new(U256::from_u64(value))
    }
    fn address(value: u64) -> Address {
        U160::from_u64(value).into()
    }

    #[test]
    fn decimals_test() {
        let api = ulm::mock::UlmMock::new();

        let erc20 = Erc20::new(api);

        assert_eq!(18, erc20.decimals());
    }

    #[test]
    fn name_test() {
        let api = ulm::mock::UlmMock::new();

        let erc20 = Erc20::new(api);

        assert_eq!("Dogecoin", erc20.name());
    }

    #[test]
    fn symbol_test() {
        let api = ulm::mock::UlmMock::new();

        let erc20 = Erc20::new(api);

        assert_eq!("DOGE", erc20.symbol());
    }

    #[test]
    fn mint_test() {
        let api = ulm::mock::UlmMock::new();

        let erc20 = Erc20::new(api);

        let account1 = address(123);
        let account2 = address(456);

        assert_eq!(balance(0), erc20.balance_of(&account1));
        assert_eq!(balance(0), erc20.balance_of(&account2));
        assert_eq!(balance(0), erc20.total_supply());

        erc20.mint(&account1, &balance(1000));

        assert_eq!(balance(1000), erc20.balance_of(&account1));
        assert_eq!(balance(0), erc20.balance_of(&account2));
        assert_eq!(balance(1000), erc20.total_supply());

        erc20.mint(&account2, &balance(2000));

        assert_eq!(balance(1000), erc20.balance_of(&account1));
        assert_eq!(balance(2000), erc20.balance_of(&account2));
        assert_eq!(balance(3000), erc20.total_supply());
    }

    #[test]
    fn transfer_test() {
        let api = ulm::mock::UlmMock::new();

        let erc20 = Erc20::new(api.clone());

        let account1 = address(123);
        let account2 = address(456);

        (*(api.borrow_mut())).set_caller(account1.clone());

        assert_eq!(balance(0), erc20.balance_of(&account1));
        assert_eq!(balance(0), erc20.balance_of(&account2));
        assert_eq!(balance(0), erc20.total_supply());

        erc20.mint(&account1, &balance(1000));

        assert_eq!(balance(1000), erc20.balance_of(&account1));
        assert_eq!(balance(0), erc20.balance_of(&account2));
        assert_eq!(balance(1000), erc20.total_supply());

        erc20.transfer(&account2, &balance(200));

        assert_eq!(balance(800), erc20.balance_of(&account1));
        assert_eq!(balance(200), erc20.balance_of(&account2));
        assert_eq!(balance(1000), erc20.total_supply());

        let api_result = api.borrow();
        assert_eq!(1, api_result.log.len());
        assert_eq!(3, api_result.log[0].indexed_fields.len());
        assert_eq!(
            vec![
                18 , 77 , 182, 52 , 90 , 145, 127, 172,
                177, 59 , 159, 146, 140, 132, 227, 44 ,
                17 , 91 , 63 , 82 , 12 , 4  , 3  , 40 ,
                230, 157, 210, 99 , 154, 105, 86 , 253,
            ],
            api_result.log[0].indexed_fields[0]
        );
        assert_eq!(
            vec![
                123_u8, 0_u8, 0_u8, 0_u8, 0_u8, 0_u8, 0_u8, 0_u8,
                0_u8, 0_u8, 0_u8, 0_u8, 0_u8, 0_u8, 0_u8, 0_u8,
                0_u8, 0_u8, 0_u8, 0_u8, 0_u8, 0_u8, 0_u8, 0_u8,
                0_u8, 0_u8, 0_u8, 0_u8, 0_u8, 0_u8, 0_u8, 0_u8,
            ],
            api_result.log[0].indexed_fields[1]
        );
        assert_eq!(
            vec![
                200_u8, 1_u8, 0_u8, 0_u8, 0_u8, 0_u8, 0_u8, 0_u8,
                0_u8, 0_u8, 0_u8, 0_u8, 0_u8, 0_u8, 0_u8, 0_u8,
                0_u8, 0_u8, 0_u8, 0_u8, 0_u8, 0_u8, 0_u8, 0_u8,
                0_u8, 0_u8, 0_u8, 0_u8, 0_u8, 0_u8, 0_u8, 0_u8,
            ],
            api_result.log[0].indexed_fields[2]
        );
        let data = api_result.log[0].data.clone();
        let b = data.slice(0..data.len());
        let expected = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc8";
        assert_eq!(expected, &b[..])
    }

    #[test]
    fn transfer_from_test() {
        let api = ulm::mock::UlmMock::new();

        let erc20 = Erc20::new(api.clone());

        let account1 = address(123);
        let account2 = address(456);
        let account3 = address(789);

        (*(api.borrow_mut())).set_caller(account1.clone());

        assert_eq!(balance(0), erc20.balance_of(&account1));
        assert_eq!(balance(0), erc20.balance_of(&account2));
        assert_eq!(balance(0), erc20.balance_of(&account3));
        assert_eq!(balance(0), erc20.total_supply());
        assert_eq!(balance(0), erc20.allowance(&account1, &account2));
        assert_eq!(balance(0), erc20.allowance(&account1, &account3));
        assert_eq!(balance(0), erc20.allowance(&account2, &account1));
        assert_eq!(balance(0), erc20.allowance(&account2, &account3));
        assert_eq!(balance(0), erc20.allowance(&account3, &account1));
        assert_eq!(balance(0), erc20.allowance(&account3, &account2));

        erc20.mint(&account1, &balance(1000));

        assert_eq!(balance(1000), erc20.balance_of(&account1));
        assert_eq!(balance(0), erc20.balance_of(&account2));
        assert_eq!(balance(0), erc20.balance_of(&account3));
        assert_eq!(balance(1000), erc20.total_supply());
        assert_eq!(balance(0), erc20.allowance(&account1, &account2));
        assert_eq!(balance(0), erc20.allowance(&account1, &account3));
        assert_eq!(balance(0), erc20.allowance(&account2, &account1));
        assert_eq!(balance(0), erc20.allowance(&account2, &account3));
        assert_eq!(balance(0), erc20.allowance(&account3, &account1));
        assert_eq!(balance(0), erc20.allowance(&account3, &account2));

        erc20.approve(&account2, &balance(300));

        assert_eq!(balance(1000), erc20.balance_of(&account1));
        assert_eq!(balance(0), erc20.balance_of(&account2));
        assert_eq!(balance(0), erc20.balance_of(&account3));
        assert_eq!(balance(1000), erc20.total_supply());
        assert_eq!(balance(300), erc20.allowance(&account1, &account2));
        assert_eq!(balance(0), erc20.allowance(&account1, &account3));
        assert_eq!(balance(0), erc20.allowance(&account2, &account1));
        assert_eq!(balance(0), erc20.allowance(&account2, &account3));
        assert_eq!(balance(0), erc20.allowance(&account3, &account1));
        assert_eq!(balance(0), erc20.allowance(&account3, &account2));

        (*(api.borrow_mut())).set_caller(account2.clone());

        erc20.transfer_from(&account1, &account3, &balance(200));

        assert_eq!(balance(800), erc20.balance_of(&account1));
        assert_eq!(balance(0), erc20.balance_of(&account2));
        assert_eq!(balance(200), erc20.balance_of(&account3));
        assert_eq!(balance(1000), erc20.total_supply());
        assert_eq!(balance(100), erc20.allowance(&account1, &account2));
        assert_eq!(balance(0), erc20.allowance(&account1, &account3));
        assert_eq!(balance(0), erc20.allowance(&account2, &account1));
        assert_eq!(balance(0), erc20.allowance(&account2, &account3));
        assert_eq!(balance(0), erc20.allowance(&account3, &account1));
        assert_eq!(balance(0), erc20.allowance(&account3, &account2));

        erc20.transfer_from(&account1, &account2, &balance(100));

        assert_eq!(balance(700), erc20.balance_of(&account1));
        assert_eq!(balance(100), erc20.balance_of(&account2));
        assert_eq!(balance(200), erc20.balance_of(&account3));
        assert_eq!(balance(1000), erc20.total_supply());
        assert_eq!(balance(0), erc20.allowance(&account1, &account2));
        assert_eq!(balance(0), erc20.allowance(&account1, &account3));
        assert_eq!(balance(0), erc20.allowance(&account2, &account1));
        assert_eq!(balance(0), erc20.allowance(&account2, &account3));
        assert_eq!(balance(0), erc20.allowance(&account3, &account1));
        assert_eq!(balance(0), erc20.allowance(&account3, &account2));
    }
}
