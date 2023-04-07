import * as React from 'react';
import { useQuery } from 'react-query';
import { useLocation, useNavigate } from 'react-router-dom';

import AppBar from '@mui/material/AppBar';
import Avatar from '@mui/material/Avatar';
import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import IconButton from '@mui/material/IconButton';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';

import { getMaterials } from '@/api/admin';
import { getAllMaterials } from '@/api/client';
import { useCurrentUser } from '@/cache/common';
import routes from '@/routes';
import { useAuth } from '@/store/auth';

import logo from './logo.png';
import { Image } from './styled';

function stringToColor(string: string) {
  let hash = 0;
  let i;

  /* eslint-disable no-bitwise */
  for (i = 0; i < string.length; i += 1) {
    hash = string.charCodeAt(i) + ((hash << 5) - hash);
  }

  let color = '#';

  for (i = 0; i < 3; i += 1) {
    const value = (hash >> (i * 8)) & 0xff;
    color += `00${value.toString(16)}`.slice(-2);
  }
  /* eslint-enable no-bitwise */

  return color;
}

function stringAvatar(name?: string) {
  if (!name) return;
  const isFullName = name.split(' ').length > 1;
  const firstname = name.split(' ')[0][0];
  const secondname = isFullName ? name.split(' ')[1][0] : '';

  return {
    sx: {
      bgcolor: stringToColor(name),
    },
    children: `${firstname}${secondname}`,
  };
}

function ResponsiveAppBar() {
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const { logout, isLogged } = useAuth();
  const { data: user } = useCurrentUser(isLogged);
  const { data: materials } = useQuery(
    'materials-yougth',
    () =>
      user?.user_status === 0
        ? getMaterials({ is_download: true, course: '6' })
        : getAllMaterials({ is_download: true, course: 6 }),
    { enabled: !!user },
  );
  const hasYouthAccess =
    materials?.find((m) => String(m.course) === '6') && user?.user_status !== 0;
  const [anchorElUser, setAnchorElUser] = React.useState<null | HTMLElement>(null);

  const handleOpenUserMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorElUser(event.currentTarget);
  };

  const handleCloseUserMenu = () => {
    setAnchorElUser(null);
  };

  const goToProfile = () => {
    handleCloseUserMenu();
    navigate({ pathname: routes[1].path });
  };

  const goHome = () => {
    handleCloseUserMenu();
    navigate({ pathname: '/' });
  };

  const goToStatistic = () => {
    handleCloseUserMenu();
    navigate({ pathname: routes[2].path });
  };

  const goToYough = () => {
    handleCloseUserMenu();
    navigate({ pathname: routes[3].path });
  };

  const goTopenalties = () => {
    handleCloseUserMenu();
    navigate({ pathname: routes[4].path });
  };

  const goToGraphics = () => {
    handleCloseUserMenu();
    navigate({ pathname: routes[5].path });
  };

  return (
    <AppBar
      position="static"
      sx={{
        bgcolor: '#fff',
        boxShadow: 'none',
        borderBottom: isLogged ? '1px solid #000' : 'none',
        py: isLogged ? 0.5 : 1,
        mt: isLogged ? 0 : 1,
      }}
    >
      <Container maxWidth="xl">
        <Toolbar
          disableGutters
          sx={{
            display: 'flex',
            justifyContent: isLogged ? 'space-between' : 'center',
            ml: isLogged ? '0' : 3,
            width: '100%',
          }}
        >
          <Image
            src={logo}
            alt="logo"
            onClick={goHome}
            sx={{
              display: { xs: 'none', md: 'flex' },
              fontWeight: 300,
              color: 'inherit',
              textDecoration: 'none',
            }}
          />

          <Image
            src={logo}
            alt="logo"
            onClick={goHome}
            sx={{
              display: { xs: 'flex', md: 'none' },
              color: 'inherit',
              textDecoration: 'none',
            }}
          />

          <Box sx={{ flexGrow: 0, visibility: isLogged ? 'visible' : 'hidden' }}>
            <IconButton onClick={handleOpenUserMenu} sx={{ p: 0 }}>
              <Avatar
                {...stringAvatar(user?.first_name)}
                sx={{
                  bgcolor: '#fff',
                  color: '#000',
                  textTransform: 'uppercase',
                  border: '1px solid #000',
                }}
              />
            </IconButton>
            <Menu
              sx={{ mt: '45px' }}
              id="menu-appbar"
              anchorEl={anchorElUser}
              anchorOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
              keepMounted
              transformOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
              open={Boolean(anchorElUser)}
              onClose={handleCloseUserMenu}
            >
              {pathname !== routes[0].path && (
                <MenuItem onClick={goHome}>
                  <Typography textAlign="center">Главная</Typography>
                </MenuItem>
              )}
              {pathname !== routes[1].path && (
                <MenuItem onClick={goToProfile}>
                  <Typography textAlign="center">Мой Профиль</Typography>
                </MenuItem>
              )}
              {pathname !== routes[5].path && user?.user_status === 2 && (
                <MenuItem onClick={goToGraphics}>
                  <Typography textAlign="center">Моя Статистика</Typography>
                </MenuItem>
              )}
              {pathname !== routes[2].path && (
                <MenuItem onClick={goToStatistic}>
                  <Typography textAlign="center">Статистика Хора</Typography>
                </MenuItem>
              )}
              {pathname !== routes[3].path && hasYouthAccess && (
                <MenuItem onClick={goToYough}>
                  <Typography textAlign="center">Молодежь</Typography>
                </MenuItem>
              )}
              {pathname !== routes[4].path && (
                <MenuItem onClick={goTopenalties}>
                  <Typography textAlign="center">Предупреждения</Typography>
                </MenuItem>
              )}
              <MenuItem
                onClick={() => {
                  handleCloseUserMenu();
                  logout();
                }}
              >
                <Typography textAlign="center">Выйти</Typography>
              </MenuItem>
            </Menu>
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
}
export default ResponsiveAppBar;
